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

from datetime import datetime
from typing import TYPE_CHECKING

from .guild import Guild
from .user import User
from .missing import Maybe, MISSING

if TYPE_CHECKING:
    from discord_typings import GuildTemplateData

    from .state import State

__all__ = (
    "GuildTemplate",
)


class GuildTemplate:
    def __init__(self, data: "GuildTemplateData", state: "State") -> None:
        self._state: "State" = state
        self._update(data)

    def __repr__(self) -> str:
        return f"<GuildTemplate code={self.code} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def _update(self, data: "GuildTemplateData") -> None:
        self._data = data
        self.code: str = data["code"]
        self.name: str = data["name"]
        self.description: str | None = data["description"]
        self.usage_count: int = data["usage_count"]
        self.creator_id: int = int(data["creator_id"])
        self.creator: User = User(data["creator"], self._state)
        self.created_at: datetime = datetime.fromisoformat(data["created_at"])
        self.updated_at: datetime = datetime.fromisoformat(data["updated_at"])
        self.source_guild_id: int = int(data["source_guild_id"])
        self.serialized_source_guild: Guild = Guild(data["serialized_source_guild"], self._state)
        self.is_dirty: bool | None = data["is_dirty"]

    async def sync(self) -> "GuildTemplate":
        # TODO: implement
        raise NotImplementedError

    async def modify(self, *, name: Maybe[str] = MISSING, description: Maybe[str] = MISSING) -> "GuildTemplate":
        # TODO: implement
        raise NotImplementedError

    async def delete(self) -> None:
        # TODO: implement
        raise NotImplementedError
