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
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from .integration import Integration

from .snowflake import Snowflake

PREMIUM_TYPE = Literal[0, 1, 2, 3]
LOCALE = Literal[
    'da',
    'de',
    'en-GB',
    'en-US',
    'en-ES',
    'fr',
    'hr',
    'it',
    'lt',
    'hu',
    'nl',
    'no',
    'pl',
    'pt-BR',
    'ro',
    'fi',
    'sv-SE',
    'vi',
    'tr',
    'cs',
    'el',
    'bg',
    'ru',
    'uk',
    'hi',
    'th',
    'zh-CN',
    'ja',
    'zh-TW',
    'ko',
]


class User(TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    avatar: str | None
    bot: NotRequired[bool]
    system: NotRequired[bool]
    mfa_enabled: NotRequired[bool]
    banner: NotRequired[str | None]
    accent_color: NotRequired[int | None]
    locale: NotRequired[LOCALE]
    verified: NotRequired[bool]
    email: NotRequired[str | None]
    flags: NotRequired[int]
    premium_type: NotRequired[PREMIUM_TYPE]
    public_flags: NotRequired[int]


SERVICE = Literal[
    'battlenet',
    'ebay',
    'epicgames',
    'facebook',
    'github',
    'leagueoflegends',
    'paypal',
    'playstation',
    'reddit',
    'riotgames',
    'spotify',
    'skype',
    'steam',
    'twitch',
    'twitter',
    'xbox',
    'youtuve',
]
VISIBILITY = Literal[0, 1]


class Connection(TypedDict):
    id: str
    name: str
    type: SERVICE
    revoked: NotRequired[bool]
    integrations: NotRequired[list[Integration]]
    verified: bool
    friend_sync: bool
    show_activity: bool
    two_way_link: bool
    visibility: int
