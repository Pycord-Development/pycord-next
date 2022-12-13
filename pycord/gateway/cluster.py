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
from multiprocessing import Process
from typing import TYPE_CHECKING

from aiohttp import BasicAuth

from ..utils import chunk
from .manager import ShardManager

if TYPE_CHECKING:
    from ..state import State


class ShardCluster(Process):
    def __init__(
        self,
        state: State,
        shards: list[int],
        amount: int,
        managers: int,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.shard_managers: list[ShardManager] = []
        self._state = state
        self._shards = shards
        self._amount = amount
        self._managers = managers
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        super().__init__()

    async def _run(self) -> None:
        await self._state._cluster_lock.acquire()
        # this is guessing that `i` is a shard manager
        tasks = []
        for sharder in list(chunk(self._shards, self._managers)):
            manager = ShardManager(
                self._state, sharder, self._amount, self._proxy, self._proxy_auth
            )
            tasks.append(manager.start())
            self.shard_managers.append(manager)
            asyncio.create_task(manager.start())
        self._state._cluster_lock.release()
        self.keep_alive = asyncio.Future()
        await self.keep_alive

    def run(self) -> None:
        asyncio.create_task(self._run())
