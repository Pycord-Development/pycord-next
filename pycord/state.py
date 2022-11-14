# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
# Copyright (c) 2022-present Pycord Development
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

if TYPE_CHECKING:
    from .commands.command import Command
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


class Single:
    def __init__(self, name: str, parent: GuildStore, typ: T, listable: bool = True, maximum: int | None = None) -> None:
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

    async def add(self, sf: Snowflake, obj: Any | StoresGuild) -> None:
        self._iter += 1

        if self._iter == self._maximum:
            self._parent.__stores.pop(next(iter(dict)))

        if not isinstance(obj, dict):
            self._parent.__stores[sf][self._name].append(obj)
        else:
            self._parent.__stores[sf] = obj

    async def remove(self, sf: Snowflake, obj_sf: Snowflake | None = None) -> None:
        if obj_sf:
            for o in self._parent.__stores[sf][self._name]:
                if isinstance(o, Member) and o.user.id == obj_sf or not isinstance(o, Member) and o.id == obj_sf:
                    self._parent.__stores[sf][self._name].remove(o)
                    break
        elif self._parent.__stores.get(sf):
            del self._parent.__stores[sf]

    async def bulk_remove(self, sf: Snowflake, sfs: list[Snowflake]) -> None:
        if not self.listable:
            raise KeyError('This object cannot be listed')

        for o in self._parent.__stores[sf][self._name]:
            if isinstance(o, Member) and o.user.id in sfs or not isinstance(o, Member) and o.id in sfs:
                self._parent.__stores[sf][self._name].remove(o)

    async def all(self, guild_id: Snowflake | None) -> list[T]:
        if guild_id:
            return self._parent.__stores[guild_id][self._name]
        else:
            return list(self._parent.__stores.items())

    async def get(self, guild_id: Snowflake, sf: Snowflake | None = None) -> T:
        if not sf:
            return self._parent.__stores[guild_id][self._name]
        for o in self._parent.__stores[guild_id][self._name]:
            if isinstance(o, Member) and o.user.id == sf or not isinstance(o, Member) and o.id == sf:
                return o

    async def upsert(self, sf: Snowflake, esf: Snowflake | None = None, **ups) -> None:
        guild = self.__stores.get(sf)

        if guild is None:
            self._parent.__stores[sf] = {'obj': ups['obj']}

        for n, v in ups.items():
            if not esf:
                self._parent.__stores[sf][n] = v
            elif n == 'apendv':
                await self.add(v['sf'], v['obj'])
            elif n == 'remv':
                await self.bulk_remove(sf, v)


class GuildStore:
    def __init__(self) -> None:
        self.__stores: dict[str, StoresGuild] = {}
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
        self.__stores: dict[str, StoresChannel] = {}
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
        self.cache: CacheManager = options.get('cache', CacheManager(max_messages=self.max_messages))
        self.ping = Ping()
        self.shard_managers: list[ShardManager] = []
        self.shard_clusters: list[ShardCluster] = []
        self.commands: list[Command] = []
        self._session_start_limit: dict[str, Any] | None = None
        self._clustered: bool | None = None
        # makes sure that multiple clusters don't start at once
        self._cluster_lock: asyncio.Lock = asyncio.Lock()
        self._ready: bool = False

    def bot_init(self, token: str, clustered: bool, proxy: str | None = None, proxy_auth: BasicAuth | None = None) -> None:
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
            channels: list[Channel] = [identify_channel(c, self) for c in data['channels']]
            threads: list[Thread] = [identify_channel(c, self) for c in data['channels']]
            stage_instances: list[StageInstance] = [StageInstance(st, self) for st in data['stage_instance']]
            guild_scheduled_events: list[ScheduledEvent] = [
                ScheduledEvent(se, self) for se in data['guild_scheduled_events']
            ]
            self.cache.guild.obj.add(
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

            args.append(guild)
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

            if self.cache.guild.members.exists(member.id):
                args.append(await self.cache.guild.members.get(member.id))
            else:
                args.append(None)

            await self.cache.guild.members.upsert(guild_id, member.id, ups=data)
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
            # TODO: Continue cache rewrite
            guild_id: Snowflake = Snowflake(data['guild_id'])
            ms: list[Member] = []
            for member_data in data['members']:
                member = Member(member_data, self)
                await self.cache.members.insert(f'{member.user.id}:{guild_id}', member)
                ms.append(member)
            args.append(ms)
        elif type == 'GUILD_ROLE_CREATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            await self.cache.roles.insert(f'{role.id}:{guild_id}', role)

            args.append(role)

            if await self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_UPDATE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role = Role(data['role'], self)

            args.append(role)

            if await self.cache.roles.exists(f'{role.id}:{guild_id}'):
                args.append(await self.cache.roles.capture(f'{role.id}:{guild_id}'))
            else:
                args.append(None)

            await self.cache.roles.insert(f'{role.id}:{guild_id}', role)

            if await self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)
        elif type == 'GUILD_ROLE_DELETE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            role_id: Snowflake = Snowflake(data['role_id'])

            if await self.cache.roles.exists(f'{role.id}:{guild_id}'):
                args.append(await self.cache.roles.capture(f'{role.id}:{guild_id}'))
            else:
                args.append(role_id)

            if await self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)
        # SECTION: channels #
        # TODO: threads
        elif type == 'CHANNEL_CREATE':
            channel = Channel(data, self)
            args.append(channel)
            await self.cache.channels.insert(channel.id, channel)
        elif type == 'CHANNEL_UPDATE':
            channel = Channel(data, self)
            args.append(channel)
            if await self.cache.channels.exists(channel.id):
                args.append(await self.cache.channels.capture(channel.id))
            else:
                args.append(None)
            await self.cache.channels.insert(channel.id, channel)
        elif type == 'CHANNEL_DELETE':
            channel = Channel(data, self)

            if await self.cache.channels.exists(channel.id):
                args.append(await self.cache.channels.capture(channel.id))
            else:
                args.append(None)
        elif type == 'CHANNEL_PINS_UPDATE':
            channel_id: Snowflake = Snowflake(data.get('channel_id'))

            if await self.cache.channels.exists(channel_id):
                args.append(await self.cache.channels.select(channel_id))
            else:
                args.append(channel_id)
        # SECTION: messages #
        elif type == 'MESSAGE_CREATE':
            message = Message(data, self)

            await self.cache.messages.insert(message.id, message)
            args.append(message)
        elif type == 'MESSAGE_UPDATE':
            message = Message(data, self)
            args.append(message)

            if await self.cache.messages.exists(message.id):
                args.append(await self.cache.messages.select(message.id))
            else:
                args.append(None)

            await self.cache.messages.insert(message.id, message)
        elif type == 'MESSAGE_DELETE':
            message_id: Snowflake = Snowflake(data['id'])

            if await self.cache.messages.exists(message_id):
                args.append(await self.cache.messages.select(message_id))
            else:
                args.append(message_id)
        elif type == 'MESSAGE_DELETE_BULK':
            arg: list[Message | int] = []
            for id in data['ids']:
                message_id: Snowflake = Snowflake(id)

                if await self.cache.messages.exists(message_id):
                    arg.append(await self.cache.messages.select(message_id))
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
        elif type == 'USER_UPDATE':
            user = User(data['user'], self)
            self.user = user

        await self.ping.dispatch(type, *args, commands=self.commands)
