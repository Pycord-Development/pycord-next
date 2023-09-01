# MIT License
#
# Copyright (c) 2023 Pycord
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

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from mypy_extensions import trait

if TYPE_CHECKING:
    from ..state.core import State


@trait
class GatewayProtocol:
    def __init__(self, state: State) -> None:
        ...

    async def start(self) -> None:
        ...

    async def get_guild_members(
        self,
        guild_id: int,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: list[int] = [],
        nonce: str | None = None,
    ) -> None:
        """Get members inside of a Guild.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild id of the members.
        query: :class:`str`
            The query to use. Defaults to an empty string, or all members.
        limit: :class:`int`
            Only return `limit` amount of members.
        presences: :class:`bool`
            Whether to return presences with the members.
        user_ids: list[:class:`int`]
            A list of users to return the member objects of.
        nonce: :class:`str`
            A custom nonce to replace Pycord's own unique nonce.
        """


class Gateway(GatewayProtocol):
    def __init__(self, state: State) -> None:
        self._state = state

    async def get_guild_members(
        self,
        guild_id: int,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: list[int] = [],
        nonce: str | None = None,
    ) -> None:
        pass
