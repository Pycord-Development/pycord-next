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
from typing import Any, TypeVar

from .flags import Intents
from .gateway import ShardManager
from .guild import Guild
from .interface import print_banner, start_logging
from .state import State
from .user import User

T = TypeVar('T')


class Bot:
    def __init__(
        self,
        intents: Intents,
        print_banner_on_startup: bool = True,
        logging_flavor: int | str | dict[str, Any] | None = None,
        max_messages: int = 1000,
        shards: int = 1,
    ) -> None:
        self.intents: Intents = intents
        self.max_messages: int = max_messages
        self._state: State = State(intents=self.intents, max_messages=self.max_messages)
        self._shards: int = shards
        self._logging_flavor: int | str | dict[str, Any] = logging_flavor
        self.user: User | None = None
        self._print_banner = print_banner_on_startup

    async def _run_async(self, token: str) -> None:
        start_logging(flavor=self._logging_flavor)
        self._state.bot_init(token=token)
        sharder = ShardManager(self._state, self._shards, self._shards)
        await sharder.start()
        self._state.shard_managers.append(sharder)
        while not self._state.raw_user:
            self._state._raw_user_fut: asyncio.Future[None] = asyncio.Future()
            await self._state._raw_user_fut

        self.user = self._state.user

        if self._print_banner:
            print_banner(self._state._session_start_limit['remaining'], self._shards, bot_name=self.user.name)

        try:
            await asyncio.Future()
        except (asyncio.CancelledError, KeyboardInterrupt):
            while True:
                await self._state.http.close_session()
                for sm in self._state.shard_managers:
                    await sm.session.close()
                return

    def run(self, token: str) -> None:
        asyncio.run(self._run_async(token=token))

    def listen(self, name: str) -> T:
        def wrapper(func: T) -> T:
            self._state.ping.add_listener(name=name, func=func)
            return func

        return wrapper

    @property
    def guilds(self) -> list[Guild]:
        return self._state.cache.guilds.all()
