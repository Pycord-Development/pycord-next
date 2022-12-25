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

from .commands import Group
from .errors import NoIdentifiesLeft, OverfilledShardsException
from .flags import Intents
from .gateway import PassThrough, ShardCluster, ShardManager
from .guild import Guild
from .interface import print_banner, start_logging
from .state import State
from .types import AsyncFunc
from .user import User
from .utils import chunk

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
    logging_flavor: Union[int, str, dict[str, Any], None]
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
        shards: int | list[int] = 1,
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

    @property
    def user(self) -> User:
        return self._state.user

    async def _run_async(self, token: str) -> None:
        start_logging(flavor=self._logging_flavor)
        self._state.bot_init(
            token=token, clustered=False, proxy=self._proxy, proxy_auth=self._proxy_auth
        )
        shards = (
            self._shards
            if isinstance(self._shards, list)
            else list(range(self._shards))
        )
        sharder = ShardManager(
            self._state,
            shards,
            self._shards,
            proxy=self._proxy,
            proxy_auth=self._proxy_auth,
        )
        await sharder.start()
        self._state.shard_managers.append(sharder)
        while not self._state.raw_user:
            self._state._raw_user_fut: asyncio.Future[None] = asyncio.Future()
            await self._state._raw_user_fut

        if self._print_banner:
            print_banner(
                self._state._session_start_limit['remaining'],
                self._shards if isinstance(self._shards, int) else len(self._shards),
                bot_name=self.user.name,
            )

        await self._run_until_exited()

    async def _run_until_exited(self) -> None:
        try:
            await asyncio.Future()
        except (asyncio.CancelledError, KeyboardInterrupt):
            # most things are already handled by the asyncio.run function
            # the only thing we have to worry about are aiohttp errors
            while True:
                await self._state.http.close_session()
                for sm in self._state.shard_managers:
                    await sm.session.close()

                if self._state._clustered:
                    for sc in self._state.shard_clusters:
                        sc.keep_alive.set_result(None)
                return

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

        if session_start_limit['remaining'] == 0:
            raise NoIdentifiesLeft('session_start_limit has been exhausted')

        self._state.shard_concurrency = PassThrough(
            session_start_limit['max_concurrency'], 7
        )
        self._state._session_start_limit = session_start_limit

        shards = (
            self._shards
            if isinstance(self._shards, list)
            else list(range(self._shards))
        )

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

    def listen(self, name: str) -> T:
        """
        Listen to an event

        Parameters
        ----------
        name: :class:`str`
            The name of the event to listen to.
        """

        def wrapper(func: T) -> T:
            self._state.ping.add_listener(name=name, func=func)
            return func

        return wrapper

    def command(self, name: str, cls: T, **kwargs: Any) -> T:
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
            command = cls(func, name, state=self._state, **kwargs)
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
