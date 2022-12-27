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

from __future__ import annotations

from typing import TYPE_CHECKING

from .color import Color
from .flags import Permissions
from .snowflake import Snowflake
from .types import Role as DiscordRole, RoleTags as DiscordRoleTags
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class RoleTags:
    def __init__(self, data: DiscordRoleTags) -> None:
        self.bot_id: UndefinedType | Snowflake = (
            Snowflake(data.get('bot_id'))
            if data.get('bot_id', UNDEFINED) is not UNDEFINED
            else UNDEFINED
        )
        self.integration_id: UndefinedType | Snowflake = (
            Snowflake(data.get('integration_id'))
            if data.get('integration_id', UNDEFINED) is not UNDEFINED
            else UNDEFINED
        )
        self.premium_subscriber: UndefinedType | None = data.get(
            'premium_subscriber', UNDEFINED
        )


class Role:
    def __init__(self, data: DiscordRole, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.color: Color = Color(data['color'])
        self.hoist: bool = data['hoist']
        self.icon: str | None | UndefinedType = data.get('icon', UNDEFINED)
        self.unicode_emoji: str | None | UndefinedType = data.get(
            'unicode_emoji', UNDEFINED
        )
        self.position: int = data['position']
        self.permissions: Permissions = Permissions.from_value(data['permissions'])
        self.managed: bool = data['managed']
        self.mentionable: bool = data['mentionable']
        self._tags: dict[str, str | None] | UndefinedType = data.get('tags', UNDEFINED)
        self.tags: RoleTags | UndefinedType = (
            RoleTags(self._tags) if self._tags is not UNDEFINED else UNDEFINED
        )
