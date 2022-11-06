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
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Callable, Coroutine, TypeVar

from aiohttp import BasicAuth

from .api import HTTPClient
from .channel import Channel
from .gateway.ping import Ping
from .guild import Guild
from .member import Member
from .message import Message
from .user import User
from .snowflake import Snowflake
from .role import Role

if TYPE_CHECKING:
    from .flags import Intents
    from .gateway import PassThrough, ShardManager

__all__ = ['State']


T = TypeVar('T')


class LimitedDict(OrderedDict):
    _limit: int = 1

    def __setitem__(self, *args, **kwargs) -> None:
        self._check_limit()
        super().__setitem__(*args, **kwargs)

    def _check_limit(self) -> None:
        if len(self.items()) == self._limit:
            del self[next(iter(self))]


# TODO: Fix types
class StateStore:
    def __init__(self, stored: T, limit: int | None = None) -> None:
        self._stored = stored
        if limit:
            self._store = LimitedDict()
            self._store._limit = limit
        else:
            self._store: dict[str, Any] = {}

    async def invoke(self, func: Callable | Coroutine, *args, **kwargs) -> T:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def _select(self, id: str | int) -> T | None:
        return self._store.get(id)

    def _capture(self, id: str | int) -> T:
        return self._store.pop(id)

    def _insert(self, id: str | int, data: T) -> None:
        self._store[id] = data

    def _exists(self, id: str | int) -> bool:
        return self.select(id=id) is not None

    def _all(self) -> list[T]:
        return [v for _, v in self._store.items()]

    async def select(self, id: str | int) -> T | None:
        return await self.invoke(self._select, id)

    async def capture(self, id: str | int) -> T:
        return await self.invoke(self._capture, id)

    async def insert(self, id: str | int, data: T) -> None:
        return await self.invoke(self._insert, id, data)

    async def exists(self, id: str | int) -> bool:
        return await self.invoke(self._exists, id)

    async def all(self) -> list[T]:
        return await self.invoke(self._all)


class CacheManager:
    def __init__(self, max_messages: int) -> None:
        self.guilds: StateStore = StateStore(Guild)
        self.members: StateStore = StateStore(Member)
        self.messages: StateStore = StateStore(Message, limit=max_messages)
        self.channels: StateStore = StateStore(Channel)
        self.roles: StateStore = StateStore(Role)

    def reset(self, max_messages: int) -> None:
        self.guilds: StateStore = StateStore(Guild)
        self.members: StateStore = StateStore(Member)
        self.messages: StateStore = StateStore(Message, limit=max_messages)
        self.channels: StateStore = StateStore(Channel)
        self.roles: StateStore = StateStore(Role)


class State:
    def __init__(self, **options: Any) -> None:
        self.options = options
        self.max_messages: int = options.get('max_messages', 1000)
        self.large_threshold: int = options.get('large_threshold', 250)
        self.shard_concurrency: PassThrough | None = None
        self.intents: Intents = options['intents']
        self.user: User | None = None
        self.raw_user: dict[str, Any] | None = None
        self.cache: CacheManager = options.get('cache', CacheManager(max_messages=self.max_messages))
        self.ping = Ping()
        self.shard_managers: list[ShardManager] = []
        self._session_start_limit: dict[str, Any] | None = None

    def bot_init(self, token: str, proxy: str | None = None, proxy_auth: BasicAuth | None = None) -> None:
        self.token = token
        self.http = HTTPClient(
            token=token,
            base_url=self.options.get('http_base_url', 'https://discord.com/api/v10'),
            proxy=proxy,
            proxy_auth=proxy_auth,
        )

    def reset(self) -> None:
        self.cache.reset(max_messages=self.max_messages)

    async def _process_event(self, type: str, data: dict[str, Any]) -> None:
        args = []

        # SECTION: guilds #
        if type == 'GUILD_CREATE':
            guild = Guild(data=data, state=self)
            args.append(guild)
            await self.cache.guilds.insert(guild.id, data=data)
        elif type == 'GUILD_UPDATE':
            guild = Guild(data=data, state=self)
            args.append(guild)

            if self.cache.guilds.exists(guild.id):
                args.append(await self.cache.guilds.capture(guild.id))
            else:
                args.append(None)

            await self.cache.guilds.insert(guild.id, guild)
        elif type == 'GUILD_DELETE':
            if await self.cache.guilds.exists(int(data['id'])):
                args.append(await self.cache.guilds.capture(int(data['id'])))
            else:
                args.append(int(data['id']))
        elif type == 'GUILD_BAN_ADD':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            if self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_BAN_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            if self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))
        elif type == 'GUILD_MEMBER_ADD':
            member = Member(data, self)
            self.cache.members.insert(f'{member.user.id}:{guild_id}', member)
            args.append(member)
        elif type == 'GUILD_MEMBER_UPDATE':
            member = Member(data, self)
            args.append(member)
            if await self.cache.members.exists(f'{member.user.id}:{guild_id}'):
                args.append(await self.cache.members.capture(f'{member.user.id}:{guild_id}'))
            else:
                args.append(None)

            await self.cache.members.insert(f'{member.user.id}:{guild_id}', member)
        elif type == 'GUILD_MEMBER_REMOVE':
            guild_id: Snowflake = Snowflake(data['guild_id'])
            if await self.cache.guilds.exists(guild_id):
                args.append(await self.cache.guilds.select(guild_id))
            else:
                args.append(guild_id)

            args.append(User(data['user'], self))

            if await self.cache.members.exists(f'{member.user.id}:{guild_id}'):
                args.append(await self.cache.members.capture(f'{member.user.id}:{guild_id}'))
            else:
                args.append(None)
        elif type == 'GUILD_MEMBERS_CHUNK':
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
        # SECTION: misc #
        elif type == 'READY':
            user = User(data['user'], self)
            self.user = user

            if hasattr(self, '_raw_user_fut'):
                self._raw_user_fut.set_result(None)
        elif type == 'USER_UPDATE':
            user = User(data['user'], self)
            self.user = user

        await self.ping.dispatch(type, *args)
