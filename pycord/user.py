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
from .enums import PremiumType
from .flags import UserFlags
from .snowflake import Snowflake
from .types import (
    LOCALE,
    User as DiscordUser,
)
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class User:
    def __init__(self, data: DiscordUser, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['username']
        self.discriminator: str = data['discriminator']
        self._avatar: str | None = data['avatar']
        self.bot: bool | UndefinedType = data.get('bot', UNDEFINED)
        self.system: bool | UndefinedType = data.get('system', UNDEFINED)
        self.mfa_enabled: bool | UndefinedType = data.get('mfa_enabled', UNDEFINED)
        self._banner: UndefinedType | str | None = data.get('banner', UNDEFINED)
        self._accent_color: UndefinedType | int | None = data.get(
            'accent_color', UNDEFINED
        )
        self.accent_color: UndefinedType | Color | None = (
            Color(self._accent_color)
            if self._accent_color not in [UNDEFINED, None]
            else self._accent_color
        )
        self.locale: UndefinedType | LOCALE = data.get('locale', UNDEFINED)
        self.verified: UndefinedType | bool = data.get('verified', UNDEFINED)
        self.email: str | None | UndefinedType = data.get('email', UNDEFINED)
        self._flags: UndefinedType | int = data.get('flags', UNDEFINED)
        self.flags: UndefinedType | UserFlags = (
            UserFlags.from_value(self._flags)
            if self._flags is not UNDEFINED
            else UNDEFINED
        )
        self._premium_type: UndefinedType | int = data.get('premium_type', UNDEFINED)
        self.premium_type: PremiumType | UndefinedType = (
            PremiumType(self._premium_type)
            if self._premium_type is not UNDEFINED
            else UNDEFINED
        )
        self._public_flags: UndefinedType | int = data.get('public_flags', UNDEFINED)
        self.public_flags: UndefinedType | UserFlags = (
            UserFlags.from_value(self._public_flags)
            if self._public_flags is not UNDEFINED
            else UNDEFINED
        )
