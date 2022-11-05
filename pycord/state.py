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

if TYPE_CHECKING:
    from .flags import Intents
    from .gateway import PassThrough, ShardCluster, ShardManager

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

    def select(self, id: str | int) -> T | None:
        return self._store.get(id)

    def capture(self, id: str | int) -> T:
        return self._store.pop(id)

    def insert(self, id: str | int, data: T) -> None:
        self._store[id] = data

    def exists(self, id: str | int) -> bool:
        return self.select(id=id) is not None

    def all(self) -> list[T]:
        return [v for _, v in self._store.items()]


class CacheManager:
    def __init__(self, max_messages: int) -> None:
        self.guilds: StateStore = StateStore(Guild)
        self.members: StateStore = StateStore(Member)
        self.messages: StateStore = StateStore(Message, limit=max_messages)
        self.channels: StateStore = StateStore(Channel)

    def reset(self, max_messages: int) -> None:
        self.guilds: StateStore = StateStore(Guild)
        self.members: StateStore = StateStore(Member)
        self.messages: StateStore = StateStore(Message, limit=max_messages)
        self.channels: StateStore = StateStore(Channel)


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
        self.shard_clusters: list[ShardCluster] = []
        self._session_start_limit: dict[str, Any] | None = None
        self._clustered: bool | None = None

    def bot_init(self, token: str, clustered: bool, proxy: str | None = None, proxy_auth: BasicAuth | None = None) -> None:
        self.token = token
        self.http = HTTPClient(
            token=token,
            base_url=self.options.get('http_base_url', 'https://discord.com/api/v10'),
            proxy=proxy,
            proxy_auth=proxy_auth,
        )
        self._clustered = clustered

    def reset(self) -> None:
        self.cache.reset(max_messages=self.max_messages)

    async def _process_event(self, type: str, data: dict[str, Any]) -> None:
        args = []

        if type in {'GUILD_CREATE', 'GUILD_UPDATE'}:
            guild = Guild(data=data, state=self)
            args.append(guild)
            self.cache.guilds.insert(int(data['id']), guild)
        elif type == 'GUILD_DELETE':
            if self.cache.guilds.exists(int(data['id'])):
                args.append(self.cache.guilds.select(int(data['id'])))
                self.cache.guilds.capture(int(data['id']))
            else:
                args.append(int(data['id']))
        elif type == 'READY':
            user = User(data['user'], self)
            self.user = user

            if hasattr(self, '_raw_user_fut'):
                self._raw_user_fut.set_result(None)

        await self.ping.dispatch(type, *args)
