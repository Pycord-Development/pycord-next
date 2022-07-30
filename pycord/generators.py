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
from typing import TYPE_CHECKING, AsyncIterator, TypeVar

from discord_typings import MessageData, Snowflake

from pycord.errors import NoMoreItems

if TYPE_CHECKING:
    from pycord.abc import Messageable

T = TypeVar('T')


class BaseAsyncGenerator(AsyncIterator[T]):
    __slots__ = ()

    async def next(self) -> T:
        raise NotImplementedError

    async def flatten(self) -> list[T]:
        return [element async for element in self]

    async def __anext__(self) -> T:
        try:
            return await self.next()
        except NoMoreItems:
            raise StopAsyncIteration

class MessageableHistoryGenerator(BaseAsyncGenerator[MessageData]):
    def __init__(
        self, 
        messageable: Messageable, 
        limit: int | None = None, 
        around: Snowflake = ...,
        before: Snowflake = ...,
        after: Snowflake = ...,
    ):
        self.around = around
        self.before = before
        self.after = after
        self.limit = limit
        self.retrieve = 0

        self.reverse = after is not None
        self.messageable = messageable
        self.channel_id: Snowflake | None = None
        self.messages = asyncio.Queue()

    async def next(self) -> MessageData:
        if self.messages.empty():
            await self.fill_messages()

        try:
            return self.messages.get_nowait()
        except asyncio.QueueEmpty:
            raise NoMoreItems

    def _should_retrieve(self):
        limit = self.limit
        retrieve = 0
        if limit is None or limit > 100:
            retrieve = 100
        else:
            retrieve = limit

        self.retrieve = retrieve
        return retrieve > 0

    async def fill_messages(self):
        if not self.channel_id:
            self.channel_id = await self.messageable._get_channel_id()

        if self._should_retrieve():
            data = await self._fetch_messages()
            if len(data) < 100:
                self.limit = 0

            if self.reverse:
                data = reversed(data)

            for elem in data:
                await self.messages.put(elem)

    async def _fetch_messages(self):
        data: list[MessageData] = await self.messageable._state._app.http.get_channel_messages(
            self.channel_id,  # type: ignore
            around=self.around,  # type: ignore
            before=self.before,
            after=self.after,
            limit=self.retrieve
        )

        if len(data):
            if self.limit is not None:
                self.limit -= self.retrieve
                
            if self.before:
                self.before = int(data[-1]['id'])
            if self.after:
                self.after = int(data[0]['id'])
            if self.around:
                self.around = ...

        return data
