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

from __future__ import annotations

from pycord.mixins import AssetMixin
from pycord.state import ConnectionState
from pycord.utils import _validate_image_params

__all__ = (
    "Asset",
)


class Asset(AssetMixin):
    CDN_URL = 'https://cdn.discordapp.com'

    def __init__(self, state: ConnectionState, *, endpoint: str, key: str, animated: bool = False):
        self._state = state
        self.url = self.CDN_URL + endpoint
        self.key = key
        self.animated = animated

    def __str__(self) -> str:
        return self.url

    def __len__(self) -> int:
        return len(self.url)

    def __repr__(self) -> str:
        return f'<Asset url={self.url.replace(self.CDN_URL, "")} animated={self.animated}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Asset) and self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

    # class methods are organized by the order in which they're listed here:
    # https://discord.com/developers/docs/reference#image-formatting-cdn-endpoints

    @classmethod
    async def _from_guild_image(
        cls,
        state: ConnectionState,
        base_path: str,
        guild_id: int,
        image_hash: str,
        fmt: str = "gif",
        size: int = 1024,
    ) -> Asset:
        # valid base paths: icons, splashes, discovery-splashes, banners
        fmt, size = _validate_image_params(image_hash, fmt, size)

        return cls(
            state,
            endpoint=f'/{base_path}/{guild_id}/{image_hash}.{fmt}?size={size}',
            key=image_hash,
            animated=image_hash.startswith("a_"),
        )

    @classmethod
    async def _from_user_banner(
        cls,
        state: ConnectionState,
        user_id: int,
        banner_hash: str,
        fmt: str = "gif",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(banner_hash, fmt, size)

        return cls(
            state,
            endpoint=f'/banners/{user_id}/{banner_hash}.{fmt}?size={size}',
            key=banner_hash,
            animated=banner_hash.startswith("a_"),
        )

    @classmethod
    async def _from_default_avatar(
        cls,
        state: ConnectionState,
        user_discriminator: int,
    ) -> Asset:
        return cls(
            state,
            endpoint=f'/embed/avatars/{(key := user_discriminator % 5)}.png',
            key=str(key),
            animated=False,
        )

    @classmethod
    async def _from_user_avatar(
        cls,
        state: ConnectionState,
        user_id: int,
        avatar_hash: str,
        fmt: str = "gif",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(avatar_hash, fmt, size)

        return cls(
            state,
            endpoint=f'/avatars/{user_id}/{avatar_hash}.{fmt}?size={size}',
            key=avatar_hash,
            animated=avatar_hash.startswith("a_"),
        )

    @classmethod
    async def _from_guild_member_avatar(
        cls,
        state: ConnectionState,
        guild_id: int,
        member_id: int,
        avatar_hash: str,
        fmt: str = "gif",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(avatar_hash, fmt, size)

        return cls(
            state,
            endpoint=f'/guilds/{guild_id}/users/{member_id}/avatars/{avatar_hash}.{fmt}?size={size}',
            key=avatar_hash,
            animated=avatar_hash.startswith("a_"),
        )

    @classmethod
    async def _from_app_image(
        cls,
        state: ConnectionState,
        base_path: str,
        app_id: int,
        image_hash: str,
        fmt: str = "png",
        size: int = 1024,
    ) -> Asset:
        # valid base paths: app-icons, app-assets
        fmt, size = _validate_image_params(image_hash, fmt, size)

        return cls(
            state,
            endpoint=f'/{base_path}/{app_id}/{image_hash}.{fmt}?size={size}',
            key=image_hash,
            animated=False,
        )

    @classmethod
    async def _from_app_achievement_icon(
        cls,
        state: ConnectionState,
        app_id: int,
        achievement_id: int,
        icon_hash: str,
        fmt: str = "png",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(icon_hash, fmt, size)

        return cls(
            state,
            endpoint=f'app-assets/{app_id}/achievements/{achievement_id}/icons/{icon_hash}.{fmt}?size={size}',
            key=icon_hash,
            animated=False,
        )

    @classmethod
    async def _from_team_icon(
        cls,
        state: ConnectionState,
        team_id: int,
        icon_hash: str,
        fmt: str = "png",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(icon_hash, fmt, size)

        return cls(
            state,
            endpoint=f'team-icons/{team_id}/{icon_hash}.{fmt}?size={size}',
            key=icon_hash,
            animated=False,
        )

    @classmethod
    async def _from_role_icon(
        cls,
        state: ConnectionState,
        role_id: int,
        icon_hash: str,
        fmt: str = "png",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(icon_hash, fmt, size)

        return cls(
            state,
            endpoint=f'role-icons/{role_id}/{icon_hash}.{fmt}?size={size}',
            key=icon_hash,
            animated=False,
        )

    @classmethod
    async def _from_scheduled_event_cover(
        cls,
        state: ConnectionState,
        event_id: int,
        cover_hash: str,
        fmt: str = "png",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(cover_hash, fmt, size)

        return cls(
            state,
            endpoint=f'guild-events/{event_id}/{cover_hash}.{fmt}?size={size}',
            key=cover_hash,
            animated=False,
        )

    @classmethod
    async def _from_guild_member_banner(
        cls,
        state: ConnectionState,
        guild_id: int,
        member_id: int,
        banner_hash: str,
        fmt: str = "gif",
        size: int = 1024,
    ) -> Asset:
        fmt, size = _validate_image_params(banner_hash, fmt, size)

        return cls(
            state,
            endpoint=f'guilds/{guild_id}/users/{member_id}/banners/{banner_hash}.{fmt}?size={size}',
            key=banner_hash,
            animated=banner_hash.startswith("a_"),
        )
