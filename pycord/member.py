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

from datetime import datetime
from typing import TYPE_CHECKING

from .flags import Permissions
from .snowflake import Snowflake
from .types import GuildMember
from .undefined import UNDEFINED, UndefinedType
from .user import User

if TYPE_CHECKING:
    from .state import State


class Member:
    def __init__(self, data: GuildMember, state: State) -> None:
        self.user: User | UndefinedType = (
            User(data.get('user'), state) if data.get('user') is not None else UNDEFINED
        )
        self.nick: str | None | UndefinedType = data.get('nick', UNDEFINED)
        self._avatar: str | None | UndefinedType = data.get('avatar', UNDEFINED)
        self.roles: list[Snowflake] = [Snowflake(s) for s in data['roles']]
        self.joined_at: datetime = datetime.fromisoformat(data['joined_at'])
        self.premium_since: None | UndefinedType | datetime = (
            datetime.fromisoformat(data.get('premium_since'))
            if data.get('premium_since', UNDEFINED) not in [UNDEFINED, None]
            else data.get('premium_since', UNDEFINED)
        )
        self.deaf: bool | UndefinedType = data.get('deaf', UNDEFINED)
        self.mute: bool | UndefinedType = data.get('mute', UNDEFINED)
        self.pending: UndefinedType | bool = data.get('pending', UNDEFINED)
        self.permissions: Permissions | UndefinedType = (
            Permissions.from_value(data.get('permissions'))
            if data.get('permissions', UNDEFINED) is not UNDEFINED
            else UNDEFINED
        )
        self.communication_disabled_until: None | UndefinedType | datetime = (
            datetime.fromisoformat(data.get('communication_disabled_until'))
            if data.get('communication_disabled_until', UNDEFINED)
            not in [UNDEFINED, None]
            else data.get('communication_disabled_until', UNDEFINED)
        )
