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
import asyncio
from typing import Any, Type, TypeVar

from aiohttp import BasicAuth

from .commands import Command, Group
from .errors import NoIdentifiesLeft, OverfilledShardsException
from .flags import Intents
from .gateway import PassThrough, ShardCluster, ShardManager
from .guild import Guild
from .interface import print_banner, start_logging
from .state import State
from .user import User
from .utils import chunk

T = TypeVar('T')


class Bot:
    def __init__(
        self,
        intents: Intents,
        print_banner_on_startup: bool = True,
        logging_flavor: int | str | dict[str, Any] | None = None,
        max_messages: int = 1000,
        shards: int | list[int] = 1,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.intents: Intents = intents
        self.max_messages: int = max_messages
        self._state: State = State(intents=self.intents, max_messages=self.max_messages)
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
        self._state.bot_init(token=token, clustered=False, proxy=self._proxy, proxy_auth=self._proxy_auth)
        shards = self._shards if isinstance(self._shards, list) else list(range(self._shards))
        sharder = ShardManager(self._state, shards, self._shards, proxy=self._proxy, proxy_auth=self._proxy_auth)
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

        await self.run_until_exited()

    async def run_until_exited(self) -> None:
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
        asyncio.run(self._run_async(token=token))

    async def _run_cluster(self, token: str, clusters: int, amount: int, managers: int) -> None:
        start_logging(flavor=self._logging_flavor)
        self._state.bot_init(token=token, clustered=True, proxy=self._proxy, proxy_auth=self._proxy_auth)

        info = await self._state.http.get_gateway_bot()
        session_start_limit = info['session_start_limit']

        if session_start_limit['remaining'] == 0:
            raise NoIdentifiesLeft('session_start_limit has been exhausted')

        self._state.shard_concurrency = PassThrough(session_start_limit['max_concurrency'], 7)
        self._state._session_start_limit = session_start_limit

        shards = self._shards if isinstance(self._shards, list) else list(range(self._shards))

        sorts = list(chunk(shards, clusters))

        for cluster in sorts:
            cluster_class = ShardCluster(
                self._state, cluster, amount, managers, proxy=self._proxy, proxy_auth=self._proxy_auth
            )
            cluster_class.run()
            self._state.shard_clusters.append(cluster_class)

        while not self._state.raw_user:
            self._state._raw_user_fut: asyncio.Future[None] = asyncio.Future()
            await self._state._raw_user_fut

        if self._print_banner:
            print_banner(
                concurrency=self._state._session_start_limit['remaining'],
                shard_count=self._shards if isinstance(self._shards, int) else len(self._shards),
                bot_name=self._state.user.name,
            )

        await self.run_until_exited()

    def cluster(self, token: str, clusters: int, amount: int | None = None, managers: int | None = None) -> None:
        shards = self._shards if isinstance(self._shards, int) else len(self._shards)

        if clusters > shards:
            raise OverfilledShardsException('Cannot have more clusters than shards')

        if not amount:
            amount = shards

        if not managers:
            managers = 1

        if amount < shards:
            raise OverfilledShardsException('Cannot have a higher shard count than shard amount')

        if managers > shards:
            raise OverfilledShardsException('Cannot have more managers than shards')

        asyncio.run(self._run_cluster(token=token, clusters=clusters, amount=amount, managers=managers))

    def listen(self, name: str) -> T:
        def wrapper(func: T) -> T:
            self._state.ping.add_listener(name=name, func=func)
            return func

        return wrapper

    def command(self, name: str, cls: Type[Command], **kwargs: Any) -> T:
        def wrapper(func: T) -> T:
            command = cls(func, name, state=self._state, **kwargs)
            self._state.commands.append(command)

        return wrapper

    def group(self, name: str, cls: Type[Group], **kwargs: Any) -> T:
        def wrapper(func: T) -> T:
            return cls(func, name, state=self._state, **kwargs)

        return wrapper

    @property
    async def guilds(self) -> list[Guild]:
        return await self._state.cache.guild.obj.all()
