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

from typing import TYPE_CHECKING

from pycord.channel import DMChannel

from .asset import Asset
from .enums import PremiumType
from .flags import UserFlags
from .missing import Maybe, MISSING
from .mixins import Identifiable

if TYPE_CHECKING:
    from discord_typings import UserData

    from .state import State


__all__ = (
    "User",
)


class User(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "username",
        "discriminator",
        "global_name",
        "avatar_hash",
        "bot",
        "system",
        "mfa_enabled",
        "banner_hash",
        "accent_color",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags",
        "avatar_decoration_hash",
    )
    def __init__(self, data: "UserData", state: "State") -> None:
        self._state: "State" = state
        self._update(data)
        
    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username={self.username} discriminator={self.discriminator} "
            f"bot={self.bot} system={self.system}>"
        )
    
    def __str__(self) -> str:
        return self.global_name or f"{self.username}#{self.discriminator}"
    
    def _update(self, data: "UserData") -> None:
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self.global_name = data["global_name"]
        self.avatar_hash = data["avatar"]
        self.bot = data.get("bot", MISSING)
        self.system = data.get("system", MISSING)
        self.mfa_enabled = data.get("mfa_enabled", MISSING)
        self.banner_hash = data.get("banner", MISSING)
        self.accent_color = data.get("accent_color", MISSING)
        self.locale = data.get("locale", MISSING)
        self.verified = data.get("verified", MISSING)
        self.email = data.get("email", MISSING)
        self.flags = UserFlags.from_value(data["flags"]) if "flags" in data else MISSING
        self.premium_type = PremiumType(data["premium_type"]) if "premium_type" in data else MISSING
        self.public_flags = UserFlags.from_value(data["public_flags"]) if "public_flags" in data else MISSING
        self.avatar_decoration_hash = data.get("avatar_decoration", MISSING)

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"
    
    @property
    def display_name(self) -> str:
        return self.global_name or self.username
    
    @property
    def avatar(self) -> Asset:
        # TODO: Return Asset
        if self.avatar_hash:
            return Asset.from_user_avatar(self._state, self.id, self.avatar_hash)
        index = (int(self.discriminator) % 5) if self.discriminator != "0" else (self.id >> 22) % 6
        return Asset.from_default_user_avatar(self._state, index)
    
    @property
    def banner(self) -> Asset | None:
        return Asset.from_user_banner(self._state, self.id, self.banner_hash) if self.banner_hash else None
    
    @property
    def avatar_decoration(self) -> Asset | None:
        return Asset.from_user_avatar_decoration(self._state, self.id, self.avatar_decoration_hash) if self.avatar_decoration_hash else None
    
    async def create_dm(self) -> DMChannel:
        # TODO: implement
        raise NotImplementedError
    
    async def send(self, *args, **kwargs) -> Message:
        dm = await self.create_dm()
        return await dm.send(*args, **kwargs)
