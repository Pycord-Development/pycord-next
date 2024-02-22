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

from __future__ import annotations

from .user import User
from .asset import Asset
from .mixins import Identifiable
from .missing import Maybe, MISSING

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import EmojiData
    from .state import State

__all__ = (
    "Emoji",
)


class Emoji(Identifiable):
    """
    Represents a custom emoji.

    Attributes
    -----------
    id: :class:`int`
        The ID of the emoji.
    name: :class:`str`
        The name of the emoji.
    roles: List[:class:`int`]
        A list of roles that may use the emoji.
    user: Optional[:class:`User`]
        The user that created the emoji.
    require_colons: Optional[:class:`bool`]
        Whether the emoji requires colons to be used.
    managed: Optional[:class:`bool`]
        Whether the emoji is managed by an integration.
    animated: Optional[:class:`bool`]
        Whether the emoji is animated.
    available: Optional[:class:`bool`]
        Whether the emoji is available.
    """
    __slots__ = (
        "_state",
        "id",
        "name",
        "roles",
        "user",
        "require_colons",
        "managed",
        "animated",
        "available",
    )

    def __init__(self, data: EmojiData, state: State) -> None:
        self._state: State = state
        self._update(data)

    def __repr__(self) -> str:
        return f"<Emoji name={self.name} id={self.id}>"

    def __str__(self) -> str:
        return f"<:{self.name}:{self.id}>" if not self.animated else f"<a:{self.name}:{self.id}>"

    def _update(self, data: "EmojiData") -> None:
        self.id: int | None = int(_id) if (_id := data.get("id")) else None
        self.name: str | None = data["name"]
        self.roles: list[int] = [int(r) for r in data.get("roles", [])]
        self.user: Maybe[User] = User(user, self._state) if (user := data.get("user")) else MISSING
        self.require_colons: Maybe[bool] = data.get("require_colons", MISSING)
        self.managed: Maybe[bool] = data.get("managed", MISSING)
        self.animated: Maybe[bool] = data.get("animated", MISSING)
        self.available: Maybe[bool] = data.get("available", MISSING)

    @property
    def asset(self) -> Asset | None:
        if self.id is None:
            return None
        return Asset.from_custom_emoji(self._state, self.id, bool(self.animated))
