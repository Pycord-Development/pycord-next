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

from .application import Application
from .channel import Channel
from .enums import InviteTargetType
from .guild import Guild
from .scheduled_event import ScheduledEvent
from .types import Invite as DiscordInvite, InviteMetadata as DiscordInviteMetadata
from .undefined import UNDEFINED, UndefinedType
from .user import User

if TYPE_CHECKING:
    from .state import State


class InviteMetadata:
    def __init__(self, data: DiscordInviteMetadata) -> None:
        self.uses: int = data['uses']
        self.max_uses: int = data['max_uses']
        self.max_age: int = data['max_age']
        self.temporary: bool = data['temporary']
        self.created_at: datetime = datetime.fromisoformat(data['created_at'])


class Invite:
    def __init__(self, data: DiscordInvite, state: State) -> None:
        self.code: str = data['code']
        self.guild: Guild | UndefinedType = (
            Guild(data['guild'], state) if data.get('guild') is not None else UNDEFINED
        )
        self.channel: Channel | None = (
            Channel(data['channel'], state) if data.get('channel') is not None else None
        )
        self.inviter: User | UndefinedType = (
            User(data['inviter'], state)
            if data.get('inviter') is not None
            else UNDEFINED
        )
        self.target_type: int | UndefinedType = (
            InviteTargetType(data['target_type'])
            if data.get('target_type') is not None
            else UNDEFINED
        )
        self.target_user: User | UndefinedType = (
            User(data['target_user'], state)
            if data.get('target_user') is not None
            else UNDEFINED
        )
        self.target_application: Application | UndefinedType = (
            Application(data['target_application'], state)
            if data.get('target_application') is not None
            else UNDEFINED
        )
        self.approximate_presence_count: int | UndefinedType = data.get(
            'approximate_presence_count', UNDEFINED
        )
        self.approximate_member_count: int | UndefinedType = data.get(
            'approximate_member_count', UNDEFINED
        )
        self.expires_at: datetime | None = (
            datetime.fromisoformat(data['expires_at'])
            if data.get('expires_at') is not None
            else data.get('expires_at', UNDEFINED)
        )
        self.guild_scheduled_event: ScheduledEvent | UndefinedType = (
            ScheduledEvent(data['guild_scheduled_event'], state)
            if data.get('guild_scheduled_event') is not None
            else UNDEFINED
        )
