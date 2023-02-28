# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
import asyncio
from typing import Any, AsyncGenerator, Type, TypeVar

from aiohttp import BasicAuth

from .application_role_connection_metadata import ApplicationRoleConnectionMetadata
from .undefined import UNDEFINED, UndefinedType
from .commands.application.command import ApplicationCommand
from .commands import Group
from .enums import (
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    VerificationLevel,
)
from .errors import BotException, NoIdentifiesLeft, OverfilledShardsException
from .events.event_manager import Event
from .flags import Intents, SystemChannelFlags
from .gateway import PassThrough, ShardCluster, ShardManager
from .guild import Guild, GuildPreview
from .interface import print_banner, start_logging
from .snowflake import Snowflake
from .state import State
from .types import AsyncFunc
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .utils import chunk, get_arg_defaults

T = TypeVar('T')


class Bot:
    """
    The class for interacting with Discord with a Bot.

    Parameters
    ----------
    intents: :class:`.flags.Intents`
        The Gateway Intents to use
    print_banner_on_startup
        Whether to print the banner on startup or not
    logging_flavor: Union[int, str, dict[str, :class:`typing.Any`], None]
        The logging flavor this bot uses

        Defaults to `None`.
    max_messages: :class:`int`
        The maximum amount of Messages to cache
    shards: :class:`int` | list[:class:`int`]
        The amount of shards this bot should launch with.

        Defaults to 1.
    proxy: :class:`str` | None
        The proxy to use
    proxy_auth: :class:`aiohttp.BasicAuth` | None
        The authentication of your proxy.

        Defaults to `None`.
    global_shard_status: :class:`int`
        The amount of shards globally deployed.
        Only supported on bots not using `.cluster`.

    Attributes
    ----------
    user: :class:`.user.User`
        The user within this bot
    guilds: list[:class:`.guild.Guild`]
        The Guilds this Bot is in
    """

    def __init__(
        self,
        intents: Intents,
        print_banner_on_startup: bool = True,
        logging_flavor: int | str | dict[str, Any] | None = None,
        max_messages: int = 1000,
        shards: int | list[int] | None = None,
        global_shard_status: int | None = None,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
        verbose: bool = False,
    ) -> None:
        self.intents: Intents = intents
        self.max_messages: int = max_messages
        self._state: State = State(
            intents=self.intents, max_messages=self.max_messages, verbose=verbose
        )
        self._shards = shards
        self._logging_flavor: int | str | dict[str, Any] = logging_flavor
        self._print_banner = print_banner_on_startup
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        if shards and not global_shard_status:
            self._global_shard_status = len(shards)
        elif global_shard_status:
            self._global_shard_status = global_shard_status
        else:
            self._global_shard_status = None

    @property
    def user(self) -> User:
        return self._state.user

    async def _run_async(self, token: str) -> None:
        start_logging(flavor=self._logging_flavor)
        self._state.bot_init(
            token=token, clustered=False, proxy=self._proxy, proxy_auth=self._proxy_auth
        )

        info = await self._state.http.get_gateway_bot()
        session_start_limit = info['session_start_limit']

        self._state.shard_concurrency = PassThrough(
            session_start_limit['max_concurrency'], 7
        )
        self._state._session_start_limit = session_start_limit

        if self._shards is None:
            shards = list(range(info['shards']))
        else:
            shards: list[int] = (
                self._shards
                if isinstance(self._shards, list)
                else list(range(self._shards))
            )

        if session_start_limit['remaining'] == 0:
            raise NoIdentifiesLeft('session_start_limit has been exhausted')
        elif session_start_limit['remaining'] - len(shards) <= 0:
            raise NoIdentifiesLeft('session_start_limit will be exhausted')

        sharder = ShardManager(
            self._state,
            shards,
            self._global_shard_status or len(shards),
            proxy=self._proxy,
            proxy_auth=self._proxy_auth,
        )
        await sharder.start()
        self._state.shard_managers.append(sharder)
        while not self._state.raw_user:
            self._state._raw_user_fut: asyncio.Future[None] = asyncio.Future()
            await self._state._raw_user_fut

        if self._print_banner:
            printable_shards = 0

            if self._shards is None:
                printable_shards = len(shards)
            else:
                printable_shards = (
                    self._shards if isinstance(self._shards, int) else len(self._shards)
                )

            print_banner(
                self._state._session_start_limit['remaining'],
                printable_shards,
                bot_name=self.user.name,
            )

        await self._run_until_exited()

    async def _run_until_exited(self) -> None:
        try:
            await asyncio.Future()
        except (asyncio.CancelledError, KeyboardInterrupt):
            # most things are already handled by the asyncio.run function
            # the only thing we have to worry about are aiohttp errors
            await self._state.http.close_session()
            for sm in self._state.shard_managers:
                await sm.session.close()

            if self._state._clustered:
                for sc in self._state.shard_clusters:
                    sc.keep_alive.set_result(None)

    def run(self, token: str) -> None:
        """
        Run the Bot without being clustered.

        .. WARNING::
            This blocks permanently and doesn't allow functions after it to run

        Parameters
        ----------
        token: :class:`str`
            The authentication token of this Bot.
        """
        asyncio.run(self._run_async(token=token))

    async def _run_cluster(
        self, token: str, clusters: int, amount: int, managers: int
    ) -> None:
        start_logging(flavor=self._logging_flavor)
        self._state.bot_init(
            token=token, clustered=True, proxy=self._proxy, proxy_auth=self._proxy_auth
        )

        info = await self._state.http.get_gateway_bot()
        session_start_limit = info['session_start_limit']

        if self._shards is None:
            shards = list(range(info['shards']))
        else:
            shards = (
                self._shards
                if isinstance(self._shards, list)
                else list(range(self._shards))
            )

        if session_start_limit['remaining'] == 0:
            raise NoIdentifiesLeft('session_start_limit has been exhausted')
        elif session_start_limit['remaining'] - len(shards) <= 0:
            raise NoIdentifiesLeft('session_start_limit will be exhausted')

        self._state.shard_concurrency = PassThrough(
            session_start_limit['max_concurrency'], 7
        )
        self._state._session_start_limit = session_start_limit

        sorts = list(chunk(shards, clusters))

        for cluster in sorts:
            cluster_class = ShardCluster(
                self._state,
                cluster,
                amount,
                managers,
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
            )
            cluster_class.run()
            self._state.shard_clusters.append(cluster_class)

        while not self._state.raw_user:
            self._state._raw_user_fut: asyncio.Future[None] = asyncio.Future()
            await self._state._raw_user_fut

        if self._print_banner:
            print_banner(
                concurrency=self._state._session_start_limit['remaining'],
                shard_count=self._shards
                if isinstance(self._shards, int)
                else len(self._shards),
                bot_name=self._state.user.name,
            )

        await self._run_until_exited()

    def cluster(
        self,
        token: str,
        clusters: int,
        amount: int | None = None,
        managers: int | None = None,
    ) -> None:
        """
        Run the Bot in a clustered formation.
        Much more complex but much more scalable.

        .. WARNING:: Shouldn't be used on Bots under ~300k Guilds

        Parameters
        ----------
        token: :class:`str`
            The authentication token of this Bot.
        clusters: :class:`int`
            The amount of clusters to run.
        amount: :class:`int`
            The full amount of shards that are/will be running globally (not just on this instance.)
        managers: :class:`int` | :class:`int`
            The amount of managers to hold per cluster.

            Defaults to `None` which automatically determines the amount.
        """
        shards = self._shards if isinstance(self._shards, int) else len(self._shards)

        if clusters > shards:
            raise OverfilledShardsException('Cannot have more clusters than shards')

        if not amount:
            amount = shards

        if not managers:
            managers = 1

        if amount < shards:
            raise OverfilledShardsException(
                'Cannot have a higher shard count than shard amount'
            )

        if managers > shards:
            raise OverfilledShardsException('Cannot have more managers than shards')

        asyncio.run(
            self._run_cluster(
                token=token, clusters=clusters, amount=amount, managers=managers
            )
        )

    def listen(self, event: Event | None = None) -> T:
        """
        Listen to an event

        Parameters
        ----------
        event: :class:`Event` | None
            The event to listen to.
            Optional if using type hints.
        """

        def wrapper(func: T) -> T:
            if event:
                self._state.event_manager.add_event(event, func)
            else:
                args = get_arg_defaults(func)

                values = list(args.values())

                if len(values) != 1:
                    raise BotException(
                        'Only one argument is allowed on event functions'
                    )

                eve = values[0]

                if eve[1] is None:
                    raise BotException(
                        'Event must either be typed, or be present in the `event` parameter'
                    )

                if not isinstance(eve[1](), Event):
                    raise BotException('Events must be of type Event')

                self._state.event_manager.add_event(eve[1], func)

            return func

        return wrapper

    def wait_for(self, event: T) -> asyncio.Future[T]:
        return self._state.event_manager.wait_for(event)

    def command(
        self,
        name: str | UndefinedType = UNDEFINED,
        cls: T = ApplicationCommand,
        **kwargs: Any,
    ) -> T:
        """
        Create a command within the Bot

        Parameters
        ----------
        name: :class:`str`
            The name of the Command.
        cls: type of :class:`.commands.Command`
            The command type to instantiate.
        kwargs: dict[str, Any]
            The kwargs to entail onto the instantiated command.
        """

        def wrapper(func: AsyncFunc) -> T:
            command = cls(func, name=name, state=self._state, **kwargs)
            self._state.commands.append(command)
            return command

        return wrapper

    def group(self, name: str, cls: Type[Group], **kwargs: Any) -> T:
        """
        Create a brand-new Group of Commands

        Parameters
        ----------
        name: :class:`str`
            The name of the Group.
        cls: type of :class:`.commands.Group`
            The group type to instantiate.
        kwargs: dict[str, Any]
            The kwargs to entail onto the instantiated group.
        """

        def wrapper(func: T) -> T:
            return cls(func, name, state=self._state, **kwargs)

        return wrapper

    @property
    async def guilds(self) -> AsyncGenerator[Guild, None]:
        return await (self._state.store.sift('guilds')).get_all()

    async def get_application_role_connection_metadata_records(
        self,
    ) -> list[ApplicationRoleConnectionMetadata]:
        """Get the application role connection metadata records.

        Returns
        -------
        list[:class:`ApplicationRoleConnectionMetadata`]
            The application role connection metadata records.
        """
        data = await self._state.http.get_application_role_connection_metadata_records(
            self.user.id
        )
        return [ApplicationRoleConnectionMetadata.from_dict(record) for record in data]

    async def update_application_role_connection_metadata_records(
        self, records: list[ApplicationRoleConnectionMetadata]
    ) -> list[ApplicationRoleConnectionMetadata]:
        """Update the application role connection metadata records.

        Parameters
        ----------
        records: list[:class:`ApplicationRoleConnectionMetadata`]
            The application role connection metadata records.

        Returns
        -------
        list[:class:`ApplicationRoleConnectionMetadata`]
            The updated application role connection metadata records.
        """
        data = (
            await self._state.http.update_application_role_connection_metadata_records(
                self.user.id, [record.to_dict() for record in records]
            )
        )
        return [ApplicationRoleConnectionMetadata.from_dict(record) for record in data]

    async def create_guild(
        self,
        name: str,
        *,
        icon: bytes | UndefinedType = UNDEFINED,
        verification_level: VerificationLevel | UndefinedType = UNDEFINED,
        default_message_notifications: DefaultMessageNotificationLevel
        | UndefinedType = UNDEFINED,
        explicit_content_filter: ExplicitContentFilterLevel | UndefinedType = UNDEFINED,
        roles: list[dict] | UndefinedType = UNDEFINED,  # TODO
        channels: list[dict] | UndefinedType = UNDEFINED,  # TODO
        afk_channel_id: Snowflake | UndefinedType = UNDEFINED,
        afk_timeout: int | UndefinedType = UNDEFINED,
        system_channel_id: Snowflake | UndefinedType = UNDEFINED,
        system_channel_flags: SystemChannelFlags | UndefinedType = UNDEFINED,
    ) -> Guild:
        """Create a guild.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild.
        icon: :class:`bytes`
            The icon of the guild.
        verification_level: :class:`VerificationLevel`
            The verification level of the guild.
        default_message_notifications: :class:`DefaultMessageNotificationLevel`
            The default message notifications of the guild.
        explicit_content_filter: :class:`ExplicitContentFilterLevel`
            The explicit content filter level of the guild.
        roles: list[dict]
            The roles of the guild.
        channels: list[dict]
            The channels of the guild.
        afk_channel_id: :class:`Snowflake`
            The afk channel id of the guild.
        afk_timeout: :class:`int`
            The afk timeout of the guild.
        system_channel_id: :class:`Snowflake`
            The system channel id of the guild.
        system_channel_flags: :class:`SystemChannelFlags`
            The system channel flags of the guild.

        Returns
        -------
        :class:`Guild`
            The created guild.
        """
        data = await self._state.http.create_guild(
            name,
            icon=icon,
            verification_level=verification_level,
            default_message_notifications=default_message_notifications,
            explicit_content_filter=explicit_content_filter,
            roles=roles,
            channels=channels,
            afk_channel_id=afk_channel_id,
            afk_timeout=afk_timeout,
            system_channel_id=system_channel_id,
            system_channel_flags=system_channel_flags,
        )
        return Guild(data, self._state)

    async def get_guild(self, guild_id: Snowflake) -> Guild:
        """Get a guild.

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            The guild id.

        Returns
        -------
        :class:`Guild`
            The guild.
        """
        data = await self._state.http.get_guild(guild_id)
        return Guild(data, self._state)

    async def get_guild_preview(self, guild_id: Snowflake) -> GuildPreview:
        """Get a guild preview.

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            The guild id.

        Returns
        -------
        :class:`GuildPreview`
            The guild preview.
        """
        data = await self._state.http.get_guild_preview(guild_id)
        return GuildPreview(data, self._state)
