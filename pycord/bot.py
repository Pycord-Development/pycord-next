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

import logging

from pycord.internal.gateway import ShardManager
from pycord.rest import RESTApp
from pycord.errors import PycordException


class Bot(RESTApp):
    def __init__(
        self, intents: int, *, shards: int = 1, version: int = 10, level: int = logging.INFO, cache_timeout: int = 10000
    ) -> None:
        self.intents = intents
        self.shards = shards
        super().__init__(version=version, level=level, cache_timeout=cache_timeout)

    async def start(self, token: str):
        await super().start(token=token)
        self._state.gateway_enabled = True

        self.shard_manager = ShardManager(self.shards, self._state, self.dispatcher, self._version)
        # .run/.start already sets token to a non-None type.
        await self.shard_manager.connect(self.token)  # type: ignore

    async def close(self):
        await super().close()
        await self.shard_manager.disconnect()
