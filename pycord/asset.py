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



from typing import Literal, TYPE_CHECKING, Self
from urllib.parse import parse_qs, urlparse

from pycord.utils import form_qs

if TYPE_CHECKING:
    from .state import State

__all__ = (
    "Asset",
)

AssetFormat = Literal["png", "jpg", "jpeg", "webp", "gif", "json"]

VALID_STATIC_ASSET_FORMATS = ("png", "jpg", "jpeg", "webp", "json")
VALID_ASSET_FORMATS = VALID_STATIC_ASSET_FORMATS + ("gif",)


class Asset:
    BASE_URL = "https://cdn.discordapp.com/"

    def __init__(
            self, 
            state: State, 
            *, 
            url: str,
            animated: bool = False,
    ) -> None:
        self._state: "State" = state
        self.url = url
        self.animated = animated

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"<Asset url={self.url}>"
    
    def url_with_parameters(self, *, format: AssetFormat | None = None, size: int | None = None) -> str:
        if not format and not size:
            return self.url
        if size:
            # validate size, must be a power of 2 between 16 and 4096
            if size < 16 or size > 4096 or (size & (size - 1)):
                raise ValueError("size must be a power of 2 between 16 and 4096")
        if format:
            if format not in VALID_ASSET_FORMATS:
                raise ValueError(f"format must be one of {VALID_ASSET_FORMATS}")
            if not self.animated and format not in VALID_STATIC_ASSET_FORMATS:
                raise ValueError(f"format must be one of {VALID_STATIC_ASSET_FORMATS}")
        url = urlparse(self.url)
        if format:
            url = url._replace(path=url.path + "." + format)
        if size:
            qs = parse_qs(url.query)
            qs["size"] = [str(size)]
            url = url._replace(query=form_qs("", **qs))
        url = url.geturl()
        return url
    
    async def get(self, *, format: AssetFormat | None = None, size: int | None = None) -> bytes:
        url = self.url_with_parameters(format=format, size=size)
        return await self._state.http.get_from_cdn(url)
    
    @classmethod
    def from_custom_emoji(cls, state: State, id: int, animated: bool = False) -> Self:
        url = cls.BASE_URL + f"emojis/{id}.png"
        return cls(state, url=url, animated=animated)
    
    @classmethod
    def from_guild_icon(cls, state: State, guild_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"icons/{guild_id}/{hash}.png"
        return cls(state, url=url, animated=hash.startswith("a_"))
    
    @classmethod
    def from_guild_splash(cls, state: State, guild_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"splashes/{guild_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_guild_discovery_splash(cls, state: State, guild_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"discovery-splashes/{guild_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_guild_banner(cls, state: State, guild_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"banners/{guild_id}/{hash}.png"
        return cls(state, url=url, animated=hash.startswith("a_"))
    
    @classmethod
    def from_user_banner(cls, state: State, user_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"banners/{user_id}/{hash}.png"
        return cls(state, url=url, animated=hash.startswith("a_"))
    
    @classmethod
    def from_default_user_avatar(cls, state: State, index: int) -> Self:
        url = cls.BASE_URL + f"embed/avatars/{index}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_user_avatar(cls, state: State, user_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"avatars/{user_id}/{hash}.png"
        return cls(state, url=url, animated=hash.startswith("a_"))
    
    @classmethod
    def from_guild_member_avatar(cls, state: State, guild_id: int, user_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"guilds/{guild_id}/users/{user_id}/avatars/{hash}.png"
        return cls(state, url=url, animated=hash.startswith("a_"))
    
    @classmethod
    def from_user_avatar_decoration(cls, state: State, user_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"avatars/{user_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_application_icon(cls, state: State, application_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"app-icons/{application_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_application_cover(cls, state: State, application_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"app-icons/{application_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_application_asset(cls, state: State, application_id: int, asset_id: int) -> Self:
        url = cls.BASE_URL + f"app-assets/{application_id}/{asset_id}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_achievement_icon(cls, state: State, application_id: int, achievement_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"app-assets/{application_id}/achievements/{achievement_id}/icons/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_store_page_asset(cls, state: State, application_id: int, asset_id: int) -> Self:
        url = cls.BASE_URL + f"app-assets/{application_id}/store/{asset_id}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_sticker_pack_banner(cls, state: State, sticker_pack_banner_asset_id: int) -> Self:
        url = cls.BASE_URL + f"app-assets/710982414301790216/store/{sticker_pack_banner_asset_id}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_team_icon(cls, state: State, team_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"team-icons/{team_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_sticker(cls, state: State, sticker_id: int, format: AssetFormat) -> Self:
        url = cls.BASE_URL + f"stickers/{sticker_id}.{format}"
        return cls(state, url=url)
    
    @classmethod
    def from_role_icon(cls, state: State, role_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"role-icons/{role_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_guild_scheduled_event_cover(cls, state: State, guild_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"guild-events/{guild_id}/{hash}.png"
        return cls(state, url=url)
    
    @classmethod
    def from_guild_member_banner(cls, state: State, guild_id: int, user_id: int, hash: str) -> Self:
        url = cls.BASE_URL + f"banners/{guild_id}/{user_id}/{hash}.png"
        return cls(state, url=url)
        