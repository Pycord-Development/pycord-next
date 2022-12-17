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
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar

from aiohttp import BasicAuth

from .types.application_commands import ApplicationCommand

from .api import HTTPClient
from .auto_moderation import AutoModRule
from .channel import Channel, Thread, identify_channel
from .gateway.ping import Ping
from .guild import Guild
from .integration import Integration
from .media import Emoji, Sticker
from .member import Member
from .message import Message
from .role import Role
from .scheduled_event import ScheduledEvent
from .snowflake import Snowflake
from .stage_instance import StageInstance
from .user import User
from .voice import VoiceState
from .interaction import Interaction

if TYPE_CHECKING:
    from .commands.command import Command
    from .ext.gears import Gear
    from .flags import Intents
    from .gateway import PassThrough, ShardCluster, ShardManager

__all__ = ['State']


T = TypeVar('T')


class StoresGuild(TypedDict):
    obj: Guild
    members: list[Member]
    channels: list[Channel]
    roles: list[Role]
    emojis: list[Emoji]
    auto_mod_rules: list[AutoModRule]
    scheduled_events: list[ScheduledEvent]
    stage_instances: list[StageInstance]
    stickers: list[Sticker]
    integrations: list[Integration]


class StoresChannel(TypedDict):
    obj: Channel
    messages: list[Message]
    voice_states: list[VoiceState]
    threads: list[Thread]


class SingleStoreParent:
    stores: dict[str, StoresGuild | StoresChannel]
    obj: Single


class Single:
    def __init__(
        self,
        name: str,
        parent: SingleStoreParent,
        typ: T,
        listable: bool = True,
        maximum: int | None = None,
    ) -> None:
        self._parent = parent
        self._name = name
        self.listable = listable
        self._iter: int = 0
        self._maximum = maximum

    async def exists(self, sf: Snowflake, sf_obj: Snowflake | None = None) -> None:
        if sf_obj:
            return await self.get(sf, sf_obj) is not None
        else:
            return await self.get(sf) is not None

    async def add(self, sf: Snowflake, obj: Any | StoresGuild | StoresChannel) -> None:
        self._iter += 1

        if self._iter == self._maximum:
            self._parent.stores.pop(next(iter(dict)))

        if self._parent.stores.get(sf) is None:
            self._parent.stores[sf] = {self._name: [] if self.listable else {}}

        if self.listable:
            things = self._parent.stores.get(sf)
            things = [] if things is None else things[self._name]
            for thing in things:
                if isinstance(thing, Member):
                    if thing.user.id == obj.id:
                        self._parent.stores[sf][self._name].remove(thing)
                elif thing.id == obj.id:
                    self._parent.stores[sf][self._name].remove(thing)

            self._parent.stores[sf][self._name].append(obj)
        elif self._parent.stores.get(sf):
            self._parent.stores[sf][self._name] = obj

        else:
            self._parent.stores[sf] = obj

    async def remove(self, sf: Snowflake, obj_sf: Snowflake | None = None) -> None:
        if obj_sf:
            for o in self._parent.stores[sf][self._name]:
                if (
                    isinstance(o, Member)
                    and o.user.id == obj_sf
                    or not isinstance(o, Member)
                    and o.id == obj_sf
                ):
                    self._parent.stores[sf][self._name].remove(o)
                    break
        elif self._parent.stores.get(sf):
            del self._parent.stores[sf]

    async def bulk_remove(self, sf: Snowflake, sfs: list[Snowflake]) -> None:
        if not self.listable:
            raise KeyError('This object cannot be listed')

        for o in self._parent.stores[sf][self._name]:
            if (
                isinstance(o, Member)
                and o.user.id in sfs
                or not isinstance(o, Member)
                and o.id in sfs
            ):
                self._parent.stores[sf][self._name].remove(o)

    async def all(self, guild_id: Snowflake | None) -> list[T]:
        if guild_id:
            return self._parent.stores[guild_id][self._name]
        else:
            return list(self._parent.stores.items())

    async def get(self, guild_id: Snowflake, sf: Snowflake | None = None) -> T:
        if not sf:
            o = self._parent.stores.get(guild_id)
            return None if o is None else o[self._name]
        for o in self._parent.stores[guild_id][self._name]:
            if (
                isinstance(o, Member)
                and o.user.id == sf
                or not isinstance(o, Member)
                and o.id == sf
            ):
                return o

    async def upsert(self, sf: Snowflake, esf: Snowflake | None = None, **ups) -> None:
        guild = self._parent.stores.get(sf)

        if guild is None:
            self._parent.stores[sf] = {'obj': ups['obj']}

        for n, v in ups.items():
            if not esf:
                self._parent.stores[sf][n] = v
            elif n == 'apendv':
                await self.add(v['sf'], v['obj'])
            elif n == 'remv':
                await self.bulk_remove(sf, v)


class GuildStore:
    def __init__(self) -> None:
        self.stores: dict[str, StoresGuild] = {}
        self.obj: Single = Single('obj', self, Guild, listable=False)
        self.members: Single = Single('members', self, Member)
        self.channels: Single = Single('channels', self, Channel)
        self.roles: Single = Single('roles', self, Role)
        self.emojis: Single = Single('emojis', self, Emoji)
        self.auto_mod_rules: Single = Single('auto_mod_rules', self, AutoModRule)
        self.scheduled_events: Single = Single('scheduled_event', self, ScheduledEvent)
        self.stage_instances: Single = Single('stage_instances', self, StageInstance)
        self.stickers: Single = Single('stickers', self, Sticker)
        self.integrations: Single = Single('integrations', self, Integration)


class ChannelStore:
    def __init__(self, max_messages: int | None) -> None:
        self.stores: dict[str, StoresChannel] = {}
        self.obj: Single = Single('obj', self, Channel, listable=False)
        self.messages: Single = Single('messages', self, Message, maximum=max_messages)
        self.voice_states: Single = Single('voice_states', self, VoiceState)
        self.threads: Single = Single('threads', self, Thread)


class CacheManager:
    def __init__(self, max_messages: int | None) -> None:
        self.guild: GuildStore = GuildStore()
        self.channel: ChannelStore = ChannelStore(max_messages=max_messages)

    def reset(self, max_messages: int | None) -> None:
        self.guild: GuildStore = GuildStore()
        self.channel: ChannelStore = ChannelStore(max_messages=max_messages)


class State:
    def __init__(self, **options: Any) -> None:
        self.options = options
        self.max_messages: int | None = options.get('max_messages', 1000)
        self.large_threshold: int = options.get('large_threshold', 250)
        self.shard_concurrency: PassThrough | None = None
        self.intents: Intents = options['intents']
        self.user: User | None = None
        self.raw_user: dict[str, Any] | None = None
        self.cache: CacheManager = options.get(
            'cache', CacheManager(max_messages=self.max_messages)
        )
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
        )
        self._clustered = clustered

    def reset(self, max_messages: int | None) -> None:
        self.cache.reset(max_messages=max_messages)

    async def _process_event(self, type: str, data: dict[str, Any]) -> None:
        args = []

        # SECTION: guilds #
        if type == 'GUILD_CREATE':
            guild = Guild(data, state=self)
            channels: list[Channel] = [
                identify_channel(c, self) for c in data['channels']
            ]
            threads: list[Thread] = [
                identify_channel(c, self) for c in data['channels']
            ]
            stage_instances: list[StageInstance] = [
                StageInstance(st, self) for st in data['stage_instances']
            ]
            guild_scheduled_events: list[ScheduledEvent] = [
                ScheduledEvent(se, self) for se in data['guild_scheduled_events']
            ]
            await self.cache.guild.obj.add(
                sf=guild.id,
                obj={
                    'obj': guild,
                    'members': [],
                    'channels': channels,
                    'roles': guild.roles,
                    'emojis': guild.emojis,
                    'stickers': guild.stickers,
                    'auto_mod_rules': [],
                    'scheduled_events': guild_scheduled_events,
                    'stage_instances': stage_instances,
                    'integrations': [],
                },
            )

            for thread in threads:
                if await self.cache.channel.obj.exists(thread.parent_id):
                    await self.cache.channel.threads.add(thread.id, thread)

            for channel in channels:
                obj: StoresChannel = {
                    'obj': channel,
                    'messages': [],
                    'voice_states': [],
                    'threads': [],
                }
                await self.cache.channel.obj.add(channel.id, obj)

            args.append(guild)

            if guild.id in self._available_guilds:
                type = 'GUILD_AVAILABLE'
            else:
                type = 'GUILD_JOIN'
        elif type == 'GUILD_UPDATE':
            guild = Guild(data=data, state=self)
            args.append(guild)

            if await self.cache.guild.obj.exists(guild.id):
                args.append(await self.cache.guild.obj.get(guild.id))

            await self.cache.guild.obj.upsert(guild.id, ups=data)
        elif type == 'GUILD_DELETE':
            await self.cache.guild.obj.remove(data['guild_id'])
        elif type == 'GUILD_BAN_ADD':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            if self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guild.obj.get(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_BAN_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            if await self.cache.guild.obj.exists(guild_id):
                args.append(await self.cache.guild.obj.get(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_MEMBER_ADD':
            member = Member(data, self)
            guild_id = data['guild_id']
            await self.cache.guild.members.add(Snowflake(guild_id), member)
            args.append(member)
        elif type == 'GUILD_MEMBER_UPDATE':
            member = Member(data, self)
            args.append(member)
            guild_id = Snowflake(data['guild_id'])
            args.append(guild_id)

            if await self.cache.guild.members.exists(member.user.id):
                args.append(await self.cache.guild.members.get(member.user.id))
            else:
                args.append(None)
            await self.cache.guild.members.add(guild_id, member)
        elif type == 'GUILD_MEMBER_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            member_id: Snowflake = Snowflake(data['user']['id'])
            if await self.cache.guild.obj.exists(guild_id):
                args.append(await self.cache.guild.obj.get(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))

            if await self.cache.guild.members.exists(guild_id, member_id):
                args.append(await self.cache.guild.members.get(guild_id, member_id))
            else:
                args.append(None)

            await self.cache.guild.members.remove(guild_id, member_id)
        elif type == 'GUILD_MEMBERS_CHUNK':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            ms: list[Member] = []
            for member_data in data['members']:
                member = Member(member_data, self)
                await self.cache.guild.members.add(member_data['id'], member)
                ms.append(member)
            args.append(ms)
        elif type == 'GUILD_ROLE_CREATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            await self.cache.guild.roles.add(role.id, role)

            args.append(role)

            if await self.cache.guild.obj.exists(guild_id):
                args.append(await self.cache.guild.obj.get(guild_id))
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_UPDATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            args.append(role)

            if await self.cache.guild.roles.exists(role.id):
                args.append(
                    await self.cache.guild.roles.get(guild_id=guild_id, sf=role.id)
                )
            else:
                args.append(None)

            await self.cache.roles.insert(f'{role.id}:{guild_id}', role)

            if await self.cache.guild.obj.exists(guild_id):
                args.append(await self.cache.guild.obj.get(guild_id))
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_DELETE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role_id: Snowflake = Snowflake(data['role_id'])

            if await self.cache.guild.roles.exists(guild_id, role_id):
                args.append(await self.cache.guild.roles.get(guild_id, role_id))
                await self.cache.guild.roles.remove(guild_id, role_id)
            else:
                args.append(role_id)

            if await self.cache.guild.obj.exists(guild_id):
                args.append(await self.cache.guild.obj.select(guild_id))
            else:
                args.append(guild_id)
        # SECTION: channels #
        # TODO: threads
        elif type == 'CHANNEL_CREATE':
            channel = Channel(data, self)
            args.append(channel)
            if channel.guild_id:
                await self.cache.guild.channels.add(channel.guild_id, channel)
            obj: StoresChannel = {
                'obj': channel,
                'messages': [],
                'voice_states': [],
                'threads': [],
            }
            await self.cache.channel.obj.add(channel, obj)
        elif type == 'CHANNEL_UPDATE':
            channel = Channel(data, self)
            args.append(channel)
            if await self.cache.channel.obj.exists(channel.id):
                args.append(await self.cache.channel.obj.get(channel.id))
                await self.cache.channel.obj.remove(channel.id)
            else:
                args.append(None)
            await self.cache.channel.obj.add(channel.id, channel)
        elif type == 'CHANNEL_DELETE':
            channel = Channel(data, self)

            if await self.cache.channel.obj.exists(channel.id):
                args.append(await self.cache.channel.obj.get(channel.id))
                await self.cache.channel.obj.remove(channel.id)
            else:
                args.append(None)
        elif type == 'CHANNEL_PINS_UPDATE':
            channel_id: Snowflake = Snowflake(data.get('channel_id'))

            if await self.cache.channel.obj.exists(channel_id):
                args.append(await self.cache.channel.obj.get(channel_id))
            else:
                args.append(channel_id)
        # SECTION: messages #
        elif type == 'MESSAGE_CREATE':
            message = Message(data, self)

            await self.cache.channel.messages.add(message.id, message)
            args.append(message)
        elif type == 'MESSAGE_UPDATE':
            message = Message(data, self)
            args.append(message)

            if await self.cache.channel.messages.exists(message.channel_id, message.id):
                args.append(
                    await self.cache.channel.messages.get(
                        message.channel_id, message.id
                    )
                )
            else:
                args.append(None)

            await self.cache.channel.messages.add(message.channel_id, message)
        elif type == 'MESSAGE_DELETE':
            message_id: Snowflake = Snowflake(data['id'])

            if await self.cache.channel.messages.exists(message_id):
                args.append(await self.cache.channel.messages.get(message_id))
                await self.cache.channel.messages.remove(message_id)
            else:
                args.append(message_id)
        elif type == 'MESSAGE_DELETE_BULK':
            arg: list[Message | int] = []
            for id in data['ids']:
                message_id: Snowflake = Snowflake(id)

                if await self.cache.messages.exists(message_id):
                    arg.append(await self.cache.channel.messages.get(message_id))
                    await self.cache.channel.messages.remove(message_id)
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
                    asyncio.create_task(gear.on_attach(), name=f'Attached Gear: {gear.name}')

                self._available_guilds: list[int] = [uag['id'] for uag in data['guilds']]

                self.application_commands = []
                self.application_commands.extend(await self.http.get_global_application_commands(self.user.id, True))

                for command in self.commands:
                    await command.instantiate()
        elif type == 'USER_UPDATE':
            user = User(data['user'], self)
            self.user = user

        elif type == 'INTERACTION_CREATE':
            type = 'INTERACTION'

            args.append(Interaction(data, self, True))

        await self.ping.dispatch(type, *args, commands=self.commands)
