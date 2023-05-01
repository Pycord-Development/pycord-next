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
from typing import TYPE_CHECKING, Any, TypeVar

from aiohttp import BasicAuth

from ..api import HTTPClient
from ..commands.application import ApplicationCommand
from ..events import GuildCreate
from ..events.channels import (
    ChannelCreate,
    ChannelDelete,
    ChannelPinsUpdate,
    ChannelUpdate,
    MessageBulkDelete,
    MessageCreate,
    MessageDelete,
    MessageUpdate,
)
from ..events.event_manager import EventManager
from ..events.guilds import (
    GuildBanCreate,
    GuildBanDelete,
    GuildDelete,
    GuildMemberAdd,
    GuildMemberChunk,
    GuildMemberRemove,
    GuildRoleCreate,
    GuildRoleDelete,
    GuildRoleUpdate,
    GuildUpdate,
)
from ..events.other import InteractionCreate, Ready, UserUpdate
from ..missing import MISSING
from ..ui import Component
from ..ui.house import House
from ..ui.text_input import Modal
from ..user import User
from .grouped_store import GroupedStore

T = TypeVar('T')

BASE_EVENTS = [
    Ready,
    GuildCreate,
    GuildUpdate,
    GuildDelete,
    GuildBanCreate,
    GuildBanDelete,
    GuildMemberAdd,
    GuildMemberRemove,
    GuildMemberChunk,
    GuildRoleCreate,
    GuildRoleUpdate,
    GuildRoleDelete,
    ChannelCreate,
    ChannelUpdate,
    ChannelDelete,
    ChannelPinsUpdate,
    MessageCreate,
    MessageUpdate,
    MessageDelete,
    MessageBulkDelete,
    UserUpdate,
    InteractionCreate,
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
        if comp.id not in self._component_custom_ids and comp.id is not MISSING:
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
