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

from typing import Any, Callable, Coroutine

from aiohttp import ClientSession
from discord_typings import Snowflake

from pycord.internal.http.route import Route


class Comparable:
    __slots__ = ()

    id: Snowflake

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, self.__class__) and obj.id == self.id

    def __ne__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return obj.id != self.id
        return True


class Dictable(Comparable):
    def __dict__(self) -> dict[Any, Any]:
        # this is already assigned to any subclass, but pyright doesn't know.
        return self.as_dict  # type: ignore


class Hashable(Dictable):
    __slots__ = ()

    def __hash__(self) -> int:
        return self.id >> 22  # type: ignore


class RouteCategoryMixin:
    _session: ClientSession

    async def request(
        self, method: str, route: Route, data: dict[str, Any] | None = None, reason: str | None = None, **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]] | str | None:
        ...
