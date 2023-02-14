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

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from aiohttp import BasicAuth

from ..events.guilds import GuildDelete, GuildUpdate

from ..api import HTTPClient
from ..channel import Channel, GuildChannel, Thread, identify_channel
from ..commands.application import ApplicationCommand
from ..events import GuildCreate
from ..events.event_manager import EventManager
from ..events.other import Ready
from ..interaction import Interaction
from ..message import Message
from ..snowflake import Snowflake
from ..ui import Component
from ..ui.house import House
from ..ui.text_input import Modal
from ..undefined import UNDEFINED
from ..user import User
from .grouped_store import GroupedStore

T = TypeVar('T')

BASE_EVENTS = [
    Ready,
    GuildCreate,
    GuildUpdate,
    GuildDelete
]

if TYPE_CHECKING:
    from ..commands.command import Command
    from ..ext.gears import Gear
    from ..flags import Intents
    from ..gateway import PassThrough, ShardCluster, ShardManager


class State:
    def __init__(self, **options: Any) -> None:
        self.options = options
        self.max_messages: int | None = options.get('max_messages', 1000)
        self.large_threshold: int = options.get('large_threshold', 250)
        self.shard_concurrency: PassThrough | None = None
        self.intents: Intents = options['intents']
        self.user: User | None = None
        self.raw_user: dict[str, Any] | None = None
        self.store = GroupedStore(messages_max_items=self.max_messages)
        self.event_manager = EventManager(BASE_EVENTS, self)
        self.shard_managers: list[ShardManager] = []
        self.shard_clusters: list[ShardCluster] = []
        self.commands: list[Command] = []
        self.gears: list[Gear] = []
        self._session_start_limit: dict[str, Any] | None = None
        self._clustered: bool | None = None
        # makes sure that multiple clusters don't start at once
        self._cluster_lock: asyncio.Lock = asyncio.Lock()
        self._ready: bool = False
        self.application_commands: list[ApplicationCommand] = []
        self.update_commands: bool = options.get('update_commands', True)
        self.verbose: bool = options.get('verbose', False)
        self.components: list[Component] = []
        self._component_custom_ids: list[str] = []
        self._components_via_custom_id: dict[str, Component] = {}
        self.modals: list[Modal] = []
        self.cache_guild_members: bool = options.get('cache_guild_members', True)

    def sent_modal(self, modal: Modal) -> None:
        if modal not in self.modals:
            self.modals.append(modal)

    def sent_component(self, comp: Component) -> None:
        if comp.id not in self._component_custom_ids and comp.id is not UNDEFINED:
            self.components.append(comp)
            self._component_custom_ids.append(comp.id)
            self._components_via_custom_id[comp.id] = comp
        elif comp.disabled != self._components_via_custom_id[comp.id].disabled:
            oldc = self._components_via_custom_id[comp.id]
            self.components.remove(oldc)
            self.components.append(comp)
            self._components_via_custom_id[comp.id] = comp

    def sent_house(self, house: House) -> None:
        for comp in house.components.values():
            self.sent_component(comp)

    def bot_init(
        self,
        token: str,
        clustered: bool,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.token = token
        self.http = HTTPClient(
            token=token,
            base_url=self.options.get('http_base_url', 'https://discord.com/api/v10'),
            proxy=proxy,
            proxy_auth=proxy_auth,
            verbose=self.verbose,
        )
        self._clustered = clustered

    # SECTION: channels #
    # TODO: threads
    async def _process_channel_create(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        if data.get('guild_id') is not None:
            channel = GuildChannel(data, self)
        else:
            channel = Channel(data, self)

        deps = [channel.guild_id] if getattr(channel, 'guild_id') else []
        await (self.store.sift('channels')).insert(deps, channel.id, channel)

        return (channel,), event_type

    async def _process_channel_update(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        if data.get('guild_id') is not None:
            channel = GuildChannel(data, self)
        else:
            channel = Channel(data, self)

        deps = [channel.guild_id] if getattr(channel, 'guild_id') else []
        res = await (self.store.sift('channels')).save(deps, channel.id, channel)

        return (channel, res or None), event_type

    async def _process_channel_delete(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        if data.get('guild_id') is not None:
            channel = GuildChannel(data, self)
        else:
            channel = Channel(data, self)

        deps = [channel.guild_id] if getattr(channel, 'guild_id') else []
        res = await (self.store.sift('channels')).discard(deps, channel.id)

        return (channel, res or None), event_type

    async def _process_channel_pins_update(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        channel_id: Snowflake = Snowflake(data.get('channel_id'))
        guild_id: Snowflake = Snowflake(data.get('guild_id'))

        resc = await (self.store.sift('channels')).get_without_parents(channel_id)

        if guild_id:
            resg = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if resc:
                return (resc[1], resg or None), event_type
            return (channel_id, resg or None), event_type

        if resc:
            return (resc[1], None), event_type

        return (channel_id, None), event_type

    # SECTION: messages #
    async def _process_message_create(
        self, _: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        message = Message(data, self)

        await (self.store.sift('messages')).insert(
            [message.channel_id], message.id, message
        )

        return (message,), 'message'

    async def _process_message_update(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        message = Message(data, self)

        res = await (self.store.sift('message')).save(
            [message.channel_id, message.channel.guild_id], message.id, message
        )

        return (message, res or None), event_type

    async def _process_message_delete(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        message_id: Snowflake = Snowflake(data['id'])

        res = await (self.store.sift('messages')).discard([], message_id)

        return (res or message_id,), event_type

    async def _process_message_delete_bulk(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        bulk: list[Message | int] = [
            (await (self.store.sift('messages')).discard([], message_id)) or message_id
            for message_id in (Snowflake(id) for id in data['ids'])
        ]

        return (bulk,), event_type

    # SECTION: automod #
    # SECTION: misc #
    async def _process_ready(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        if self._ready:
            return (), event_type

        user = User(data['user'], self)
        self.user = user

        if hasattr(self, '_raw_user_fut'):
            self._raw_user_fut.set_result(None)

        self._ready = True

        for gear in self.gears:
            asyncio.create_task(gear.on_attach(), name=f'Attaching Gear: {gear.name}')

        self._available_guilds: list[int] = [uag['id'] for uag in data['guilds']]

        self.application_commands = []
        self.application_commands.extend(
            await self.http.get_global_application_commands(self.user.id, True)
        )
        self._application_command_names: list[str] = []

        for command in self.commands:
            await command.instantiate()
            if hasattr(command, 'name'):
                self._application_command_names.append(command.name)

        for app_command in self.application_commands:
            if app_command['name'] not in self._application_command_names:
                await self.http.delete_global_application_command(
                    self.user.id.real, app_command['id']
                )

        return (), 'hook'

    async def _process_user_update(
        self, event_type: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        user = User(data['user'], self)
        self.user = user

        return (), event_type

    async def _process_interaction_create(
        self, _: str, data: dict[str, Any]
    ) -> tuple[tuple, str]:
        interaction = Interaction(data, self, True)

        for component in self.components:
            asyncio.create_task(component._invoke(interaction))

        for modal in self.modals:
            asyncio.create_task(modal._invoke(interaction))

        return (interaction,), 'INTERACTION'

    _events: dict[str, Callable] = {
        'CHANNEL_CREATE': _process_channel_create,
        'CHANNEL_UPDATE': _process_channel_update,
        'CHANNEL_DELETE': _process_channel_delete,
        'CHANNEL_PINS_UPDATE': _process_channel_pins_update,
        'MESSAGE_CREATE': _process_message_create,
        'MESSAGE_UPDATE': _process_message_update,
        'MESSAGE_DELETE': _process_message_delete,
        'MESSAGE_DELETE_BULK': _process_message_delete_bulk,
        'READY': _process_ready,
        'USER_UPDATE': _process_user_update,
        'INTERACTION_CREATE': _process_interaction_create,
    }

    async def _process_event(self, event_type: str, data: dict[str, Any]) -> None:
        await self.emitter.dispatch(event_type, _raw_data=data, commands=self.commands)
