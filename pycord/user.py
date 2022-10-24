# Copyright (c) 2021-2022 VincentRPS
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
# SOFTWARE.

from datetime import datetime
from typing import Protocol

from discord_typings.resources import UserData

from pycord.mixins import Hashable
from pycord.state import BaseConnectionState
from pycord.utils import _convert_base64_from_bytes, grab_creation_time


class BaseUser(Protocol):
    as_dict: UserData
    _state: BaseConnectionState

    id: int
    email: str | None
    username: str
    flags: int | None
    public_flags: int | None
    locale: str | None
    accent_color: int | None
    banner: str | None
    avatar: str | None
    discriminator: str
    premium_type: int | None
    system: bool | None
    mfa_enabled: bool | None
    verified: bool | None
    bot: bool | None

    def __init__(self, data: UserData, state: BaseConnectionState) -> None:
        pass


class BaseCurrentUser(BaseUser):
    async def edit(self, username: str | None = None, avatar: bytes | None = None) -> None:
        pass


class User(BaseUser, Hashable):
    def __init__(self, data: UserData, state: BaseConnectionState) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.email = data.get('email')
        self.username = data['username']
        self.flags = data.get('flags')
        self.public_flags = data.get('public_flags')
        self.locale = data.get('locale')
        self.accent_color = data.get('accent_color')
        self.banner = data.get('banner')
        self.avatar = data['avatar']
        self.discriminator = data['discriminator']
        self.premium_type = data.get('premium_type')
        self.system = data.get('system')
        self.mfa_enabled = data.get('mfa_enabled')
        self.verified = data.get('verified')
        self.bot = data.get('bot')

    @property
    def mention(self) -> str:
        return f'<@{self.id}>'

    @property
    def created_at(self) -> datetime:
        return grab_creation_time(self.id)  # type: ignore


class CurrentUser(User, BaseCurrentUser):
    async def edit(self, username: str | None = None, avatar: bytes | None = None) -> None:
        if not username and not avatar:
            return

        if avatar:
            avatar = _convert_base64_from_bytes(avatar)  # type: ignore

        edited = await self._state._app.http.edit_me(username=username, avatar=avatar)  # type: ignore

        self.username = edited['username']
        self.avatar = edited['avatar']
