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

from functools import cached_property
from typing import TYPE_CHECKING

from .color import Color
from .enums import PremiumType
from .flags import UserFlags
from .snowflake import Snowflake
from .types import LOCALE, User as DiscordUser
from .missing import MISSING, MissingEnum, Maybe

if TYPE_CHECKING:
    from .state import State


class User:
    def __init__(self, data: DiscordUser, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['username']
        self.discriminator: str = data['discriminator']
        self._avatar: str | None = data['avatar']
        self.bot: bool | MissingEnum = data.get('bot', MISSING)
        self.system: bool | MissingEnum = data.get('system', MISSING)
        self.mfa_enabled: bool | MissingEnum = data.get('mfa_enabled', MISSING)
        self._banner: MissingEnum | str | None = data.get('banner', MISSING)
        self._accent_color: MissingEnum | int | None = data.get(
            'accent_color', MISSING
        )
        self.accent_color: MissingEnum | Color | None = (
            Color(self._accent_color)
            if self._accent_color not in [MISSING, None]
            else self._accent_color
        )
        self.locale: MissingEnum | LOCALE = data.get('locale', MISSING)
        self.verified: MissingEnum | bool = data.get('verified', MISSING)
        self.email: str | None | MissingEnum = data.get('email', MISSING)
        self._flags: MissingEnum | int = data.get('flags', MISSING)
        self.flags: MissingEnum | UserFlags = (
            UserFlags.from_value(self._flags)
            if self._flags is not MISSING
            else MISSING
        )
        self._premium_type: MissingEnum | int = data.get('premium_type', MISSING)
        self.premium_type: PremiumType | MissingEnum = (
            PremiumType(self._premium_type)
            if self._premium_type is not MISSING
            else MISSING
        )
        self._public_flags: MissingEnum | int = data.get('public_flags', MISSING)
        self.public_flags: MissingEnum | UserFlags = (
            UserFlags.from_value(self._public_flags)
            if self._public_flags is not MISSING
            else MISSING
        )

    @cached_property
    def mention(self) -> str:
        return f'<@{self.id}>'
