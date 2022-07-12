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
import logging
from typing import Any, Callable, Coroutine

from pycord.internal import EventDispatcher, HTTPClient, start_logging
from pycord.state import ConnectionState
from pycord.user import CurrentUser


def find_loop():
    try:
        return asyncio.get_running_loop()
    except:
        return asyncio.new_event_loop()


class RESTApp:
    def __init__(self, *, version: int = 10, level: int = logging.INFO, cache_timeout: int = 10000) -> None:
        self.token: str = None
        self.cache_timeout = cache_timeout
        self._version = version
        self._level = level
        self.dispatcher = EventDispatcher()

    def run(self, token: str):
        self.token = token

        async def runner():
            await self.start()
            self.dispatcher.dispatch('hook')

        loop = find_loop()
        loop.run_until_complete(runner())
        loop.run_forever()

    async def start(self):
        start_logging(level=self._level)
        self._state = ConnectionState(self, cache_timeout=self.cache_timeout)
        await self._state.start_cache()

        http = HTTPClient(self.token, self._version)
        self.http = http
        user_data = await http.get_me()
        self.user = CurrentUser(user_data)

    async def edit(self, username: str | None = None, avatar: bytes | None = None):
        return await self.user.edit(username=username, avatar=avatar)

    @property
    async def guilds(self):
        return self._state.guilds.values()

    def listen(self, name: Any):
        def inner(func: Callable | Coroutine):
            self.dispatcher.add_listener(name=name, function=func)

        return inner
