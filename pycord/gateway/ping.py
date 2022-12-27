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

import asyncio

from ..types import AsyncFunc


class Ping:
    def __init__(self) -> None:
        self._pings: dict[str, list[AsyncFunc]] = {}
        self._temporary_pings: dict[str, list[AsyncFunc]] = {}

    async def _wrap(self, func: AsyncFunc, *args, **kwargs) -> None:
        await func(*args, **kwargs)

    async def dispatch(self, name_: str, *args, **kwargs) -> None:
        name = f'on_{name_.lower()}'

        commands = kwargs.pop('commands', [])

        for ping in self._pings.get(name, []):
            wrap = self._wrap(ping, *args, **kwargs)
            asyncio.create_task(wrap)

        for ping in self._temporary_pings.get(name, []):
            wrap = self._wrap(ping, *args, **kwargs)
            asyncio.create_task(wrap)
            self._temporary_pings[name].remove(ping)

        for command in commands:
            if command._processor_event == name:
                asyncio.create_task(command._invoke(*args, **kwargs))

    def add_listener(self, name: str, func: AsyncFunc) -> None:
        if self._pings.get(name):
            self._pings[name].append(func)
        else:
            self._pings[name] = [func]
