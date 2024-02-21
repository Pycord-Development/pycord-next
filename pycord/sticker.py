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

from .asset import Asset
from .user import User
from .enums import StickerFormatType, StickerType
from .missing import Maybe, MISSING
from .mixins import Identifiable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import StickerData, StickerPackData

    from .state import State


class Sticker(Identifiable):
    __slots__ = (
        "id",
        "pack_id",
        "name",
        "description",
        "tags",
        "type",
        "format_type",
        "available",
        "guild_id",
        "user_id",
        "sort_value",
    )

    def __init__(self, *, data: "StickerData", state: "State"):
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "StickerData"):
        self.id: int = int(data["id"])
        self.pack_id: Maybe[int] = int(pid) if (pid := data.get("pack_id")) else MISSING
        self.name: str = data["name"]
        self.description: str | None = data["description"]
        self.tags: str | None = data["tags"]
        self.type: StickerType = StickerType(data["type"])
        self.format_type: StickerFormatType = StickerFormatType(data["format_type"])
        self.available: Maybe[bool] = data.get("available", MISSING)
        self.guild_id: Maybe[int] = int(gid) if (gid := data.get("guild_id")) else MISSING
        self.user: Maybe[User] = User(data=user, state=self._state) if (user := data.get("user")) else MISSING
        self.sort_value: Maybe[int] = int(sv) if (sv := data.get("sort_value")) else MISSING

    def __repr__(self) -> str:
        return f"<Sticker id={self.id} pack_id={self.pack_id} name={self.name} description={self.description} tags={self.tags} type={self.type} format_type={self.format_type} available={self.available} guild_id={self.guild_id} user={self.user} sort_value={self.sort_value}>"

    def __str__(self) -> str:
        return self.name

    async def modify(
        self,
        *,
        name: str = None,
        description: str = None,
        tags: str = None,
        reason: str | None = None,
    ) -> "Sticker":
        if self.guild_id is None:
            raise Exception("Sticker has no guild attached")
        # TODO: implement
        raise NotImplementedError

    async def delete(self, *, reason: str | None = None) -> None:
        if self.guild_id is None:
            raise Exception("Sticker has no guild attached")
        # TODO: implement
        raise NotImplementedError

    @property
    def asset(self) -> Asset:
        formats = {
            StickerFormatType.PNG: "png",
            StickerFormatType.APNG: "apng",
            StickerFormatType.LOTTIE: "json",
        }
        return Asset.from_sticker(self._state, self.id, formats.get(self.format_type, "png"))


class StickerPack(Identifiable):
    __slots__ = (
        "id",
        "stickers",
        "name",
        "sku_id",
        "cover_sticker_id",
        "description",
        "banner_asset_id",
    )

    def __init__(self, *, data: "StickerPackData", state: "State"):
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "StickerPackData"):
        self.id: int = int(data["id"])
        self.stickers: list[Sticker] = [Sticker(data=sticker, state=self._state) for sticker in data["stickers"]]
        self.name: str = data["name"]
        self.sku_id: int = int(data["sku_id"])
        self.cover_sticker_id: Maybe[int] = int(coverid) if (coverid := data.get("cover_sticker_id")) else MISSING
        self.description: str = data["description"]
        self.banner_asset_id: Maybe[int] = int(bannerid) if (bannerid := data.get("banner_asset_id")) else MISSING

    def __repr__(self) -> str:
        return f"<StickerPack id={self.id} stickers={self.stickers} name={self.name} sku_id={self.sku_id} cover_sticker_id={self.cover_sticker_id} description={self.description} banner_asset_id={self.banner_asset_id}>"

    def __str__(self) -> str:
        return self.name

    @property
    def cover_sticker_asset(self) -> Asset | None:
        if self.cover_sticker_id is None:
            return None
        sticker = next((sticker for sticker in self.stickers if sticker.id == self.cover_sticker_id), None)
        if sticker is None:
            return None
        return sticker.asset

    @property
    def banner_asset(self) -> Asset | None:
        if self.banner_asset_id is None:
            return None
        return Asset.from_sticker_pack_banner(self._state, self.banner_asset_id, "png")
