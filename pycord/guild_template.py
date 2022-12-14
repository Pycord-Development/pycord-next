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

from .snowflake import Snowflake
from .types import GuildTemplate as DiscordGuildTemplate
from .user import User

if TYPE_CHECKING:
    from .state import State


class GuildTemplate:
    def __init__(self, data: DiscordGuildTemplate, state: State) -> None:
        self.code: str = data['code']
        self.name: str = data['name']
        self.description: str | None = data['description']
        self.usage_count: int = data['usage_count']
        self.creator_id: Snowflake = Snowflake(data['creator_id'])
        self.creator: User = User(data['creator'], state)
        self.created_at: datetime = datetime.fromisoformat(data['created_at'])
        self.updated_at: datetime = datetime.fromisoformat(data['updated_at'])
        self.source_guild_id: Snowflake = Snowflake(data['source_guild_id'])
        # TODO: maybe make this a Guild object?
        self.serialized_source_guild: dict = data['serialized_source_guild']
        self.is_dirty: bool | None = data['is_dirty']
