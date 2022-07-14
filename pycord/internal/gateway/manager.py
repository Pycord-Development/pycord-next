# Copyright (c) 2021-2022 VincentRPS
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
# SOFTWARE.
import asyncio

from pycord.state import ConnectionState

from ..events import EventDispatcher
from .shard import Shard


class ShardManager:
    def __init__(self, shards: int, state: ConnectionState, events: EventDispatcher, version: int = 10) -> None:
        self._shards = shards
        self.shards: list[Shard] = []
        self.state = state
        self.version = version
        self.events = events
        self.running = False
        self.token = ""
        self._loop_task: asyncio.Task | None = None

    async def connect(self, token: str) -> None:
        self.token = token

        for i in range(self._shards):
            shard = Shard(i, self._shards, self.state, self.events, self.version)
            await shard.connect(token=self.token)
            self.shards.append(shard)
            await asyncio.sleep(5)

        self.running = True
        self._loop_task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            try:
                for i, shard in enumerate(self.shards):
                    if shard._ws.closed and shard._reconnectable:
                        # the websocket is closed, we have to reconnect
                        await shard.connect(token=self.token)
                    elif not shard._reconnectable:
                        # we cannot reconnect, so we have to recreate the shard
                        new_shard = Shard(i, self._shards, self.state, self.events, self.version)
                        await new_shard.connect(token=self.token)
                        self.shards[i] = new_shard
            except asyncio.CancelledError:
                break

    async def disconnect(self) -> None:
        self._loop_task.cancel()
        await self._loop_task

        for shard in self.shards:
            await shard.disconnect(reconnect=False)
