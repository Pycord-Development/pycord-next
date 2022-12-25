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
from ..channel import Channel, Thread, identify_channel
from ..commands.application import ApplicationCommand
from ..gateway.ping import Ping
from ..guild import Guild
from ..interaction import Interaction
from ..member import Member
from ..message import Message
from ..role import Role
from ..scheduled_event import ScheduledEvent
from ..snowflake import Snowflake
from ..stage_instance import StageInstance
from ..ui import Component
from ..ui.house import House
from ..ui.text_input import Modal
from ..undefined import UNDEFINED
from ..user import User
from .grouped_store import GroupedStore

T = TypeVar('T')

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
        self.ping = Ping()
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

    async def _process_event(self, type: str, data: dict[str, Any]) -> None:
        args = []

        # SECTION: guilds #
        if type == 'GUILD_CREATE':
            guild = Guild(data, state=self)
            channels: list[Channel] = [
                identify_channel(c, self) for c in data['channels']
            ]
            threads: list[Thread] = [
                identify_channel(c, self) for c in data['threads']
            ]
            stage_instances: list[StageInstance] = [
                StageInstance(st, self) for st in data['stage_instances']
            ]
            guild_scheduled_events: list[ScheduledEvent] = [
                ScheduledEvent(se, self) for se in data['guild_scheduled_events']
            ]

            await (self.store.sift('guilds')).insert([guild.id], guild.id, guild)

            for channel in channels:
                await (self.store.sift('channels')).insert(
                    [guild.id], channel.id, channel
                )

            for thread in threads:
                await (self.store.sift('threads')).insert(
                    [guild.id, thread.parent_id], thread.id, thread
                )

            for stage in stage_instances:
                await (self.store.sift('stages')).insert(
                    [stage.channel_id, guild.id, stage.guild_scheduled_event_id],
                    stage.id,
                    stage,
                )

            for scheduled_event in guild_scheduled_events:
                await (self.store.sift('scheduled_events')).insert(
                    [
                        scheduled_event.channel_id,
                        scheduled_event.creator_id,
                        scheduled_event.entity_id,
                        guild.id,
                    ],
                    scheduled_event.id,
                    scheduled_event,
                )

            args.append(guild)

            if guild.id in self._available_guilds:
                type = 'GUILD_AVAILABLE'
            else:
                type = 'GUILD_JOIN'
        elif type == 'GUILD_UPDATE':
            guild = Guild(data=data, state=self)
            args.append(guild)

            res = await (self.store.sift('guilds')).save([guild.id], guild.id, guild)

            if res is not None:
                args.append(res)
            else:
                args.append(None)
        elif type == 'GUILD_DELETE':
            guild_id = Snowflake(data['guild_id'])
            res = await (self.store.sift('guilds')).discard([guild_id], guild_id)

            if res is not None:
                args.append(res)
            else:
                args.append(guild_id)
        elif type == 'GUILD_BAN_ADD':
            guild_id: Snowflake = Snowflake(data['guild_id'])

            res = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if res is not None:
                args.append(res[1])
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_BAN_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])

            res = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if res is not None:
                args.append(res[1])
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_MEMBER_ADD':
            member = Member(data, self)
            guild_id = Snowflake(data['guild_id'])
            await (self.store.sift('members')).insert(
                [guild_id], member.user.id, member
            )
            args.append(member)
        elif type == 'GUILD_MEMBER_UPDATE':
            member = Member(data, self)
            args.append(member)
            guild_id = Snowflake(data['guild_id'])
            args.append(guild_id)

            res = await (self.store.sift('members')).save(
                [guild_id], member.user.id, member
            )

            if res:
                args.append(res)
            else:
                args.append(None)
        elif type == 'GUILD_MEMBER_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            member_id: Snowflake = Snowflake(data['user']['id'])

            resg = await (self.store.sift('guilds')).get_without_parents(guild_id)
            resm = await (self.store.sift('members')).discard([guild_id], member_id)

            if resg:
                args.append(resg[1])
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))

            if resm:
                args.append(resm)
            else:
                args.append(member_id)
        elif type == 'GUILD_MEMBERS_CHUNK':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            ms: list[Member] = []
            for member_data in data['members']:
                member = Member(member_data, self)
                await (self.store.sift('members')).save(
                    [guild_id], member.user.id, member
                )
                ms.append(member)
            args.append(ms)
        elif type == 'GUILD_ROLE_CREATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            await (self.store.sift('roles')).insert([guild_id], role.id, role)

            args.append(role)

            guild = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if guild:
                args.append(guild[1])
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_UPDATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            args.append(role)

            res = await (self.store.sift('roles')).save([guild_id], role.id, role)

            if res:
                args.append(res)
            else:
                args.append(None)

            res = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if res:
                args.append(res[1])
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_DELETE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role_id: Snowflake = Snowflake(data['role_id'])

            resr = await (self.store.sift('roles')).discard([guild_id], role_id)

            if resr:
                args.append(resr)
            else:
                args.append(role_id)

            resg = await (self.store.sift('guilds')).get_without_parents(guild_id)

            if resg:
                args.append(resg[1])
            else:
                args.append(guild_id)
        # SECTION: channels #
        # TODO: threads
        elif type == 'CHANNEL_CREATE':
            channel = Channel(data, self)
            args.append(channel)
            deps = []
            if channel.guild_id:
                deps.append(channel.guild_id)

            await (self.store.sift('channels')).insert(deps, channel.id, channel)
        elif type == 'CHANNEL_UPDATE':
            channel = Channel(data, self)
            args.append(channel)

            deps = []
            if channel.guild_id:
                deps.append(channel.guild_id)

            res = await (self.store.sift('channels')).save(deps, channel.id, channel)
            if res:
                args.append(res)
            else:
                args.append(None)
        elif type == 'CHANNEL_DELETE':
            channel = Channel(data, self)

            deps = []
            if channel.guild_id:
                deps.append(channel.guild_id)

            res = await (self.store.sift('channels')).discard(deps, channel.id)

            if res:
                args.append(res)
            else:
                args.append(None)
        elif type == 'CHANNEL_PINS_UPDATE':
            channel_id: Snowflake = Snowflake(data.get('channel_id'))
            guild_id: Snowflake = Snowflake(data.get('guild_id'))

            res = await (self.store.sift('channels')).get_without_parents(channel_id)

            if res:
                args.append(res[1])
            else:
                args.append(channel_id)

            if guild_id:
                resg = await (self.store.sift('guilds')).get_without_parents(guild_id)

                if resg:
                    args.append(resg)
                else:
                    args.append(None)
            else:
                args.append(None)
        # SECTION: messages #
        elif type == 'MESSAGE_CREATE':
            message = Message(data, self)

            await (self.store.sift('messages')).insert(
                [message.channel_id], message.id, message
            )
            args.append(message)
            type = 'message'
        elif type == 'MESSAGE_UPDATE':
            message = Message(data, self)
            args.append(message)

            res = await (self.store.sift('message')).save(
                [message.channel_id, message.channel.guild_id], message.id, message
            )

            if res:
                args.append(res)
            else:
                args.append(None)
        elif type == 'MESSAGE_DELETE':
            message_id: Snowflake = Snowflake(data['id'])

            res = await (self.store.sift('messages')).discard([], message_id)

            if res:
                args.append(res)
            else:
                args.append(message_id)
        elif type == 'MESSAGE_DELETE_BULK':
            arg: list[Message | int] = []
            for id in data['ids']:
                message_id: Snowflake = Snowflake(id)

                res = await (self.store.sift('messages')).discard([], message_id)

                if res:
                    arg.append(res)
                else:
                    arg.append(message_id)
            args.append(arg)
        # SECTION: automod #
        # SECTION: misc #
        elif type == 'READY':
            if not self._ready:
                user = User(data['user'], self)
                self.user = user

                if hasattr(self, '_raw_user_fut'):
                    self._raw_user_fut.set_result(None)

                self._ready = True

                for gear in self.gears:
                    asyncio.create_task(
                        gear.on_attach(), name=f'Attaching Gear: {gear.name}'
                    )

                self._available_guilds: list[int] = [
                    uag['id'] for uag in data['guilds']
                ]

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

                await self.ping.dispatch('hook', *args, commands=self.commands)

        elif type == 'USER_UPDATE':
            user = User(data['user'], self)
            self.user = user

        elif type == 'INTERACTION_CREATE':
            type = 'INTERACTION'
            interaction = Interaction(data, self, True)
            args.append(interaction)

            for component in self.components:
                asyncio.create_task(component._invoke(interaction))

            for modal in self.modals:
                asyncio.create_task(modal._invoke(interaction))

        await self.ping.dispatch(type, *args, commands=self.commands)
