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

from .enums import StageInstancePrivacyLevel
from .snowflake import Snowflake
from .types import StageInstance as DiscordStageInstance
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class StageInstance:
    def __init__(self, data: DiscordStageInstance, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.channel_id: Snowflake = Snowflake(data['channel_id'])
        self.topic: str = data['topic']
        self.privacy_level: StageInstancePrivacyLevel = StageInstancePrivacyLevel(
            data['privacy_level']
        )
        self.guild_scheduled_event_id: UndefinedType | Snowflake = (
            Snowflake(data['guild_scheduled_event_id'])
            if data.get('guild_scheduled_event_id') is not None
            else UNDEFINED
        )
