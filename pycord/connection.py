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

from .enums import VisibilityType
from .snowflake import Snowflake
from .types import (
    SERVICE,
    Connection as DiscordConnection,
    Integration as DiscordIntegration,
)
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class Connection:
    def __init__(self, data: DiscordConnection, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.type: SERVICE = data['type']
        self.revoked: bool | UndefinedType = data.get('revoked', UNDEFINED)
        self._integrations: list[DiscordIntegration] | UndefinedType = data.get(
            'integrations', UNDEFINED
        )
        self.verified: bool = data['verified']
        self.friend_sync: bool = data['friend_sync']
        self.show_activity: bool = data['show_activity']
        self.two_way_linked: bool = data['two_way_link']
        self.visibility: VisibilityType = VisibilityType(data['visibility'])
