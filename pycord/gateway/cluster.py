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
from multiprocessing import Process

from aiohttp import BasicAuth

from ..state import State
from .manager import ShardManager


class ShardCluster(Process):
    def __init__(
        self,
        state: State,
        shards: int,
        starts_at: int | None,
        amount: int,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.shard_managers: list[ShardManager] = []
        self._state = state
        self._shards = shards
        self._starts_at = starts_at
        self._amount = amount
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        super().__init__(daemon=True)

    async def _run(self) -> None:
        # this is guessing that `i` is a shard manager
        tasks = []
        for _ in range(...):
            manager = ShardManager(self._state, self._shards, self._amount, self._starts_at, self._proxy, self._proxy_auth)
            tasks.append(manager.start())
            self.shard_managers.append(manager)
        await asyncio.gather(*tasks)

    def run(self) -> None:
        asyncio.create_task(self._run())
