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
from typing import TYPE_CHECKING, Any, TypeVar, Callable

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

    # SECTION: guilds #
    async def _process_guild_create(self, _: str, data: dict[str, Any]) -> tuple[tuple, str]:
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

        if guild.id in self._available_guilds:
            return (guild, ), 'GUILD_AVAILABLE'
        else:
            return (guild, ), 'GUILD_JOIN'

    async def _process_guild_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild = Guild(data=data, state=self)
        res = await (self.store.sift('guilds')).save([guild.id], guild.id, guild)

        if res is None:
            return (guild, None), event_type
        else:
            return (guild, res), event_type
    
    async def _process_guild_delete(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id = Snowflake(data['guild_id'])
        res = await (self.store.sift('guilds')).discard([guild_id], guild_id)

        if res is None:
            return (guild_id, ), event_type
        else:
            return (res, ), event_type
    
    async def _process_guild_ban_add(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        res = await (self.store.sift('guilds')).get_without_parents(guild_id)

        if res is None:
            return (guild_id, User(data['user'], self)), event_type
        else:
            return (res[1], User(data['user'], self)), event_type
    
    async def _process_guild_ban_remove(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        res = await (self.store.sift('guilds')).get_without_parents(guild_id)

        if res is None:
            return (guild_id, User(data['user'], self)), event_type
        else:
            return (res[1], User(data['user'], self)), event_type

    async def _process_member_add(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        member = Member(data, self)
        guild_id = Snowflake(data['guild_id'])
        await (self.store.sift('members')).insert(
            [guild_id], member.user.id, member
        )

        return (member, ), event_type

    async def _process_guild_member_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        member = Member(data, self)
        guild_id = Snowflake(data['guild_id'])

        res = await (self.store.sift('members')).save(
            [guild_id], member.user.id, member
        )

        if res:
            return (member, guild_id, res), event_type
        else:
            return (member, guild_id, None), event_type
    
    async def _process_guild_member_remove(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        member_id: Snowflake = Snowflake(data['user']['id'])

        resg = await (self.store.sift('guilds')).get_without_parents(guild_id)
        resm = await (self.store.sift('members')).discard([guild_id], member_id)
        
        user = User(data['user'], self)

        if resg:
            return (resg[1], user, resm or member_id), event_type

        elif resm:
            return (guild_id, user, resm), event_type

        return (guild_id, user, member_id), event_type

    async def _process_guild_member_chunk(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        ms: list[Member] = [
            await (self.store.sift('members')).save(
                [guild_id], member.user.id, member
            )
            for member in (
                Member(member_data, self)
                for member_data
                in data['members']
            )
        ]

        return (ms, ), event_type

    async def _process_guild_role_create(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        role = Role(data['role'], self)

        await (self.store.sift('roles')).insert([guild_id], role.id, role)
        guild = await (self.store.sift('guilds')).get_without_parents(guild_id)

        if guild:
            return (role, guild[1]), event_type
        else:
            return (role, guild_id), event_type
    
    async def _process_guild_role_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        role = Role(data['role'], self)

        resr = await (self.store.sift('roles')).save([guild_id], role.id, role)
        resg = await (self.store.sift('guilds')).get_without_parents(guild_id)

        if resr:
            return (role, resr, resg[1] if resg else guild_id), event_type

        elif resg:
            return (role, None, resg[1]), event_type
        
        return (role, None, guild_id), event_type
    
    async def _process_guild_role_delete(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        role_id: Snowflake = Snowflake(data['role_id'])

        resr = await (self.store.sift('roles')).discard([guild_id], role_id)
        resg = await (self.store.sift('guilds')).get_without_parents(guild_id)
        
        if resr:
            return (resr, resg[1] if resg else guild_id), event_type

        elif resg:
            return (role_id, resg[1]), event_type
        
        return (role_id, guild_id), event_type

    # SECTION: channels #
    # TODO: threads
    async def _process_channel_create(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        channel = Channel(data, self)

        deps = [channel.guild_id] if channel.guild_id else []
        await (self.store.sift('channels')).insert(deps, channel.id, channel)
        
        return (channel, ), event_type
    
    async def _process_channel_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        channel = Channel(data, self)

        deps = [channel.guild_id] if channel.guild_id else []
        res = await (self.store.sift('channels')).save(deps, channel.id, channel)

        return (channel, res or None), event_type
    
    async def _process_channel_delete(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        channel = Channel(data, self)

        deps = [channel.guild_id] if channel.guild_id else []
        res = await (self.store.sift('channels')).discard(deps, channel.id)

        return (channel, res or None), event_type

    async def _process_channel_pins_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
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
    async def _process_message_create(self, _: str, data: dict[str, Any]) -> tuple[tuple, str]:
        message = Message(data, self)

        await (self.store.sift('messages')).insert(
            [message.channel_id], message.id, message
        )

        return (message, ), 'message'
    
    async def _process_message_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        message = Message(data, self)

        res = await (self.store.sift('message')).save(
            [message.channel_id, message.channel.guild_id], message.id, message
        )

        return (message, res or None), event_type

    async def _process_message_delete(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        message_id: Snowflake = Snowflake(data['id'])

        res = await (self.store.sift('messages')).discard([], message_id)

        return (res or message_id, ), event_type

    async def _process_message_delete_bulk(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        bulk: list[Message | int] = [
            (await (self.store.sift('messages')).discard([], message_id))
            or message_id

            for message_id
            in (
                Snowflake(id)
                for id
                in data['ids']
            )
        ]

        return (bulk, ), event_type

    # SECTION: automod #
    # SECTION: misc #
    async def _process_ready(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        if self._ready:
            return (), event_type

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

        return (), 'hook'
    
    async def _process_user_update(self, event_type: str, data: dict[str, Any]) -> tuple[tuple, str]:
        user = User(data['user'], self)
        self.user = user
        
        return (), event_type
    
    async def _process_interaction_create(self, _: str, data: dict[str, Any]) -> tuple[tuple, str]:
        interaction = Interaction(data, self, True)

        for component in self.components:
            asyncio.create_task(component._invoke(interaction))

        for modal in self.modals:
            asyncio.create_task(modal._invoke(interaction))
        
        return (interaction, ), 'INTERACTION'

    _events: dict[str, Callable] = {
        'GUILD_CREATE': _process_guild_create,
        'GUILD_UPDATE': _process_guild_update,
        'GUILD_DELETE': _process_guild_delete,
        'GUILD_BAN_ADD': _process_guild_ban_add,
        'GUILD_BAN_REMOVE': _process_guild_ban_remove,
        'GUILD_MEMBER_ADD': _process_member_add,
        'GUILD_MEMBER_UPDATE': _process_guild_member_update,
        'GUILD_MEMBER_REMOVE': _process_guild_member_remove,
        'GUILD_MEMBERS_CHUNK': _process_guild_member_chunk,
        'GUILD_ROLE_CREATE': _process_guild_role_create,
        'GUILD_ROLE_UPDATE': _process_guild_role_update,
        'GUILD_ROLE_DELETE': _process_guild_role_delete,
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
        if event_proccessor := self._events.get(event_type, None):
            args, event_type = await event_proccessor(self, event_type, data)

            await self.ping.dispatch(event_type, *args, commands=self.commands)
