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

from pycord.user import User

from .enums import GuildScheduledEventEntityType, GuildScheduledEventPrivacyLevel, GuildScheduledEventStatus
from .missing import Maybe, MISSING
from .mixins import Identifiable
from .asset import Asset

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import GuildScheduledEventData, GuildScheduledEventEntityMetadataData

    from .state import State

__all__ = (
    "GuildScheduledEvent",
    "GuildScheduledEventEntityMetadata",
)


class GuildScheduledEvent(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
        "image_hash",
    )

    def __init__(self, data: "GuildScheduledEventData", state: "State") -> None:
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "GuildScheduledEventData") -> None:
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.channel_id: int | None = int(cid) if (cid := data.get("channel_id")) else None
        self.creator_id: int | None = int(crid) if (crid := data.get("creator_id")) else None
        self.name: str = data["name"]
        self.description: Maybe[str | None] = data.get("description", MISSING)
        self.scheduled_start_time: datetime = datetime.fromisoformat(data["scheduled_start_time"])
        self.scheduled_end_time: datetime | None = datetime.fromisoformat(end) if (
            end := data.get("scheduled_end_time")) else None
        self.privacy_level: GuildScheduledEventPrivacyLevel = GuildScheduledEventPrivacyLevel(data["privacy_level"])
        self.status: GuildScheduledEventStatus = GuildScheduledEventStatus(data["status"])
        self.entity_type: GuildScheduledEventEntityType = GuildScheduledEventEntityType(data["entity_type"])
        self.entity_id: int | None = int(eid) if (eid := data.get("entity_id")) else None
        self.entity_metadata: GuildScheduledEventEntityMetadata | None = GuildScheduledEventEntityMetadata.from_data(
            mdata
            ) if (mdata := data.get("entity_metadata")) else None
        self.creator: Maybe[User] = User(data=data["creator"], state=self._state) if (data.get("creator")) else MISSING
        self.user_count: Maybe[int] = data.get("user_count", MISSING)
        self.image_hash: Maybe[str] = data.get("image", MISSING)

    @property
    def cover_image(self) -> Asset | None:
        return Asset.from_guild_scheduled_event_cover(
            self._state, self.guild_id, self.image_hash
            ) if self.image_hash else None

    async def modify(self, **kwargs) -> "GuildScheduledEvent":
        # TODO: Implement
        raise NotImplementedError

    async def delete(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    async def get_users(self) -> list[User]:
        # TODO: Implement
        raise NotImplementedError


class GuildScheduledEventEntityMetadata:
    __slots__ = (
        "location",
    )

    def __init__(self, *, location: Maybe[str] = MISSING) -> None:
        self.location: Maybe[str] = location

    @classmethod
    def from_data(cls, data: "GuildScheduledEventEntityMetadataData") -> "GuildScheduledEventEntityMetadata":
        return cls(**data)

    def __repr__(self) -> str:
        return f"<GuildScheduledEventEntityMetadata location={self.location!r}>"

    def __str__(self) -> str:
        return self.__repr__()
