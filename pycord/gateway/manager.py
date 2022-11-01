# cython: language_level=3
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

from aiohttp import ClientSession

from ..errors import NoIdentifiesLeft
from ..state import State
from .notifier import Notifier
from .passthrough import PassThrough
from .shard import Shard


class BaseShardManager:
    shards: list[Shard]
    session: ClientSession
    _state: State
    _out_of: int
    _max_shards: int
    _shard_start_number: int

    def __init__(
        self, state: State, max_shards: int, shard_start_number: int = 0
    ) -> None:
        ...

    def add_shard(self, shard: Shard) -> None:
        ...

    def remove_shard(self, shard: Shard) -> None:
        ...

    def remove_shards(self) -> None:
        ...

    async def delete_shard(self, shard: Shard) -> None:
        ...

    async def delete_shards(self) -> None:
        ...

    async def start(self) -> None:
        ...

    async def shutdown(self) -> None:
        ...


class ShardManager(BaseShardManager):
    def __init__(
        self, state: State, max_shards: int, out_of: int, shard_start_number: int = 0
    ) -> None:
        self.shards: list[Shard] = []
        self._state = state
        self._out_of = out_of
        self._max_shards = max_shards
        self._shard_start_number = shard_start_number

    def add_shard(self, shard: Shard) -> None:
        self.shards.insert(shard.id, shard)

    def remove_shard(self, shard: Shard) -> None:
        self.shards.remove(shard)

    def remove_shards(self) -> None:
        self.shards.clear()

    async def delete_shard(self, shard: Shard) -> None:
        shard._receive_task.cancel()
        shard._hb_task.set_result(None)

        await shard._ws.close()
        self.remove_shard(shard)

    async def delete_shards(self) -> None:
        for shard in self.shards:
            await self.delete_shard(shard=shard)

    async def start(self) -> None:
        self.session = ClientSession()
        notifier = Notifier(self)

        if not self._state.shard_concurrency:
            info = await self._state.http.get_gateway_bot()
            session_start_limit = info['session_start_limit']

            if session_start_limit['remaining'] == 0:
                raise NoIdentifiesLeft('session_start_limit has been exhausted')

            self._state.shard_concurrency = PassThrough(
                session_start_limit['max_concurrency'], 7
            )

        tasks = []

        for shard_id in range(self._max_shards):
            if shard_id < self._shard_start_number:
                continue

            shard = Shard(
                id=shard_id, state=self._state, session=self.session, notifier=notifier
            )

            tasks.append(shard.connect(token=self._state.token))

            self.shards.append(shard)

        await asyncio.gather(*tasks)

    async def shutdown(self) -> None:
        await self.delete_shards()
