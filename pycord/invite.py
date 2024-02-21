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

from .application import Application
from .asset import Asset
from .emoji import Emoji
from .enums import (
    DefaultMessageNotificationLevel, ExplicitContentFilterLevel, InviteTargetType, MFALevel, NSFWLevel,
    PremiumTier, VerificationLevel,
)
from .flags import Permissions, SystemChannelFlags, RoleFlags
from .guild_scheduled_event import GuildScheduledEvent
from .missing import Maybe, MISSING
from .mixins import Identifiable
from .user import User

if TYPE_CHECKING:
    from discord_typings import InviteData, InviteStageInstanceData

    from .state import State

__all__ = (
    "Invite",
    "InviteStageInstance",
)


class Invite:
    def __init__(self, data: "InviteData", state: "State") -> None:
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "InviteData") -> None:
        self.code: str = data["code"]
        self.guild_id: Maybe[int] = data.get("guild_id", MISSING)
        self.channel: Channel | None = Channel(channel, self._state) if (channel := data.get("channel")) else None
        self.inviter: Maybe[User] = User(inviter, self._state) if (inviter := data.get("inviter")) else MISSING
        self.target_type: Maybe[InviteTargetType] = InviteTargetType(data.get("target_type")) if (
            data.get("target_type")) else MISSING
        self.target_user: Maybe[User] = User(target_user, self._state) if (
            target_user := data.get("target_user")) else MISSING
        self.target_application: Maybe[Application] = Application(target_application, self._state) if (
            target_application := data.get("target_application")) else MISSING
        self.approximate_presence_count: Maybe[int] = data.get("approximate_presence_count", MISSING)
        self.approximate_member_count: Maybe[int] = data.get("approximate_member_count", MISSING)
        self.expires_at: Maybe[datetime | None] = datetime.fromisoformat(expires) if (expires := data.get(
            "expires_at", MISSING
            )) not in (None, MISSING) else expires
        self.stage_instance: Maybe[InviteStageInstance] = InviteStageInstance(stage_instance, self._state) if (
            stage_instance := data.get("stage_instance")) else MISSING
        self.guild_scheduled_event: Maybe[GuildScheduledEvent] = GuildScheduledEvent(
            guild_scheduled_event, self._state
            ) if (guild_scheduled_event := data.get("guild_scheduled_event")) else MISSING


class InviteStageInstance:
    def __init__(self, data: "InviteStageInstanceData", state: "State") -> None:
        self.members: list[Member] = [Member(member, state) for member in data["members"]]
        self.participant_count: int = data["participant_count"]
        self.speaker_count: int = data["speaker_count"]
        self.topic: str = data["topic"]
