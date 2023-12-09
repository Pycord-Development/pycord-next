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



from .enums import StageInstancePrivacyLevel
from .mixins import Identifiable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import StageInstanceData

    from .state import State


class StageInstance(Identifiable):
    __slots__ = (
        "id",
        "guild_id",
        "channel_id",
        "topic",
        "privacy_level",
        "discoverable_disabled",
        "guild_scheduled_event_id",
    )

    def __init__(self, *, data: "StageInstanceData", state: "State"):
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "StageInstanceData"):
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.channel_id: int = int(data["channel_id"])
        self.topic: str = data["topic"]
        self.privacy_level: StageInstancePrivacyLevel = StageInstancePrivacyLevel(data["privacy_level"])
        self.discoverable_disabled: bool = data["discoverable_disabled"]
        self.guild_scheduled_event_id: int | None = int(gseid) if (gseid := data.get("guild_scheduled_event_id")) else None

    def __repr__(self) -> str:
        return f"<StageInstance id={self.id} guild_id={self.guild_id} channel_id={self.channel_id} topic={self.topic} privacy_level={self.privacy_level} discoverable_disabled={self.discoverable_disabled} guild_scheduled_event_id={self.guild_scheduled_event_id}>"
    
    async def modify(
            self, 
            *, 
            topic: str = None, 
            privacy_level: StageInstancePrivacyLevel = None, 
            discoverable_disabled: bool = None,
            reason: str | None = None,
    ) -> "StageInstance":
        # TODO: implement
        raise NotImplementedError
    
    async def delete(self, *, reason: str | None = None) -> None:
        # TODO: implement
        raise NotImplementedError