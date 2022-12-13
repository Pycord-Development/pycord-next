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

from .member import Member
from .snowflake import Snowflake
from .types import VoiceState as DiscordVoiceState
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class VoiceState:
    def __init__(self, data: DiscordVoiceState, state: State) -> None:
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data['guild_id'])
            if data.get('guild_id') is not None
            else UNDEFINED
        )
        self.channel_id: Snowflake | None = (
            Snowflake(data['channel_id'])
            if data.get('channel_id') is not None
            else None
        )
        self.user_id: Snowflake = Snowflake(data['user_id'])
        self.member: Member | UndefinedType = (
            Member(data['member'], state)
            if data.get('member') is not None
            else UNDEFINED
        )
        self.session_id: str = data['session_id']
        self.deaf: bool = data['deaf']
        self.mute: bool = data['mute']
        self.self_deaf: bool = data['self_deaf']
        self.self_mute: bool = data['self_mute']
        self.self_stream: bool | UndefinedType = data.get('self_stream', UNDEFINED)
        self.self_video: bool = data['self_video']
        self.suppress: bool = data['suppress']
        self.request_to_speak: datetime | UndefinedType = (
            datetime.fromisoformat(data['request_to_speak_timestamp'])
            if data.get('request_to_speak_timestamp') is not None
            else None
        )
