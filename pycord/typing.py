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
from typing import TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    from .abc import Messageable

class Typing:
    def __init__(self, messageable: "Messageable") -> None:
        self.messageable = messageable
        self._task: asyncio.Task | None = None

    async def perform_typing(self):
        channel_id = await self.messageable._get_channel_id()
        trigger_typing = self.messageable._state._app.http.trigger_typing_indicator

        while True:
            await trigger_typing(channel_id)
            await asyncio.sleep(10)

    async def __aenter__(self: Self) -> Self:
        self._task = asyncio.create_task(self.perform_typing())
        return self

    # we use args here to abstract the other parameters we don't care about
    async def __aexit__(self, *args):
        if self._task:
            self._task.cancel()
            await self._task
