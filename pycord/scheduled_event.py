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
from typing import TYPE_CHECKING, Any

from .enums import (
    GuildScheduledEventEntityType,
    GuildScheduledEventPrivacyLevel,
    GuildScheduledEventStatus,
)
from .member import Member
from .snowflake import Snowflake
from .types import EntityMetadata as DiscordEntityMetadata, GuildScheduledEvent
from .missing import MISSING, MissingEnum, Maybe
from .user import User

if TYPE_CHECKING:
    from .state import State


class EntityMetadata:
    def __init__(self, data: DiscordEntityMetadata) -> None:
        self.location: MissingEnum | str = data.get('location', MISSING)


class ScheduledEventUser:
    def __init__(self, data: dict[str, Any], state: State) -> None:
        self.guild_scheduled_event_id: Snowflake = Snowflake(
            data['guild_scheduled_event_id']
        )
        self.user: User = User(data['user'], state)
        self.member: Member | MissingEnum = (
            Member(data['member'], state)
            if data.get('member') is not None
            else MISSING
        )


class ScheduledEvent:
    def __init__(self, data: GuildScheduledEvent, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self._channel_id: str | None = data.get('channel_id')
        self.channel_id: Snowflake | None = (
            Snowflake(self._channel_id) if self._channel_id is not None else None
        )
        self._creator_id: MissingEnum | None | str = data.get('creator_id', MISSING)
        self.creator_id: MissingEnum | None | Snowflake = (
            Snowflake(self._creator_id)
            if isinstance(self._creator_id, str)
            else self._creator_id
        )
        self.name: str = data['name']
        self.description: MissingEnum | str | None = data.get(
            'description', MISSING
        )
        self.scheduled_start_time: datetime = datetime.fromisoformat(
            data['scheduled_start_time']
        )
        self._scheduled_end_time: str | None = data.get('scheduled_end_time')
        self.scheduled_end_time: datetime | None = (
            datetime.fromisoformat(self._scheduled_end_time)
            if self._scheduled_end_time is not None
            else None
        )
        self.privacy_level: GuildScheduledEventPrivacyLevel = (
            GuildScheduledEventPrivacyLevel(data['privacy_level'])
        )
        self.status: GuildScheduledEventStatus = GuildScheduledEventStatus(
            data['status']
        )
        self.entity_type: GuildScheduledEventEntityType = GuildScheduledEventEntityType(
            data['entity_type']
        )
        self._entity_id: str | None = data.get('entity_id')
        self.entity_id: Snowflake | None = (
            Snowflake(self._entity_id) if self._entity_id is not None else None
        )
        self._entity_metadata: dict[str, Any] | MissingEnum = data.get(
            'entity_metadata', MISSING
        )
        self.entity_metadata: EntityMetadata | MissingEnum = (
            EntityMetadata(self._entity_metadata)
            if self._entity_metadata is not MISSING
            else MISSING
        )
        self._creator: dict[str, Any] | MissingEnum = data.get('creator', MISSING)
        self.creator: User | MissingEnum = (
            User(self._creator, state) if self._creator is not MISSING else MISSING
        )
        self.user_count: int | MissingEnum = data.get('user_count', MISSING)
        self._image: None | str | MissingEnum = data.get('image', MISSING)
