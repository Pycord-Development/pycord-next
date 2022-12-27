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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .snowflake import Snowflake
from .user import User


class Emoji(TypedDict):
    id: Snowflake | None
    name: str
    roles: NotRequired[list[Snowflake]]
    user: NotRequired[User]
    require_colons: NotRequired[bool]
    managed: NotRequired[bool]
    animated: NotRequired[bool]
    available: NotRequired[bool]


class StickerItem(TypedDict):
    id: Snowflake
    name: str
    format_type: Literal[1, 2, 3]


class Sticker(StickerItem):
    pack_id: NotRequired[Snowflake]
    description: str | None
    tags: str
    asset: NotRequired[str]
    type: Literal[1, 2]
    available: NotRequired[bool]
    guild_id: NotRequired[Snowflake]
    user: NotRequired[User]
    sort_value: NotRequired[int]


class StickerPack(TypedDict):
    id: Snowflake
    stickers: list[Sticker]
    name: str
    sku_id: Snowflake
    cover_sticker_id: NotRequired[Snowflake]
    description: str
    banner_asset_id: NotRequired[Snowflake]


class Attachment(TypedDict):
    id: Snowflake
    filename: str
    description: NotRequired[str]
    content_type: NotRequired[str]
    size: int
    url: str
    proxy_url: str
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    ephemeral: NotRequired[bool]
