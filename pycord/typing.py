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


import typing
from typing import TYPE_CHECKING, Any

from .types.snowflake import Snowflake

if TYPE_CHECKING:
    from .state import State


class Typing:
    def __init__(self, channel_id: Snowflake, state: "State") -> None:
        self._state = state
        self.__channel_id = channel_id

    async def trigger(self) -> None:
        await self._state.http.trigger_typing_indicator(self.__channel_id)

    async def __aenter__(self) -> typing.Self:
        await self.trigger()
        return self

    async def __aexit__(self, exc_t: Any, exc_v: Any, exc_tb: Any) -> None:
        await self.trigger()
