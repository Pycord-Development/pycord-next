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
from types import EllipsisType
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

async def channel_history_generator(
    messageable: 'Messageable',
    limit: int | None = None,
    around: Snowflake = ...,
    before: Snowflake = ...,
    after: Snowflake = ...,
):
    _around: Snowflake | EllipsisType = around
    retrieve = 0
    reverse = after is not ...
    channel_id = await messageable._get_channel_id()

    def should_retrieve():
        if limit is None or limit > 100:
            retrieve = 100
        else:
            retrieve = limit
        return retrieve > 0

    while should_retrieve():
        get_msg_args = {
            'before': before,
            'after': after,
            'limit': retrieve
        }
        if _around is not ...:
            get_msg_args['around'] = _around

        data = await messageable._state._app.http.get_channel_messages(
            channel_id,
            **get_msg_args,
        )

        if len(data):
            if limit is not None:
                limit -= retrieve

            if before is not ...:
                before = int(data[-1]['id'])
            if after is not ...:
                after = int(data[0]['id'])
            if around is not ...:
                _around = ...

            if len(data) < 100:
                limit = 0

        if reverse:
            data = reversed(data)

        for msg in data:
            yield msg
