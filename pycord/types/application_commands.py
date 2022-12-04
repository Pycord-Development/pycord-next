# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
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

from .channel import CTYPE
from .snowflake import Snowflake
from .user import LOCALE

ATYPE = Literal[
    1,
    2,
    3,
]
AOTYPE = Literal[
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
]


class ApplicationCommandOptionChoice(TypedDict):
    name: str
    name_localizations: NotRequired[dict[LOCALE, str] | None]
    value: str | int | float


class ApplicationCommandOption(TypedDict):
    type: ATYPE
    name: str
    name_localizations: NotRequired[dict[LOCALE, str] | None]
    description: str
    description_localizations: NotRequired[dict[LOCALE, str] | None]
    required: NotRequired[bool]
    choices: NotRequired[ApplicationCommandOptionChoice]
    options: NotRequired[list["ApplicationCommandOption"]]
    channel_types: NotRequired[list[CTYPE]]
    min_value: NotRequired[int]
    max_value: NotRequired[int]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]


class ApplicationCommand(TypedDict):
    id: Snowflake
    type: NotRequired[ATYPE]
    application_id: Snowflake
    guild_id: NotRequired[Snowflake]
    name: str
    name_localizations: NotRequired[dict[LOCALE, str] | None]
    description: str
    description_localizations: NotRequired[dict[LOCALE, str] | None]
    options: NotRequired[list[ApplicationCommandOption]]
    default_member_permissions: str | None
    dm_permission: NotRequired[bool]
    default_permission: NotRequired[bool | None]
    version: Snowflake


class ApplicationCommandPermissions(TypedDict):
    id: Snowflake
    type: Literal[1, 2, 3]
    permission: bool


class GuildApplicationCommandPermissions(TypedDict):
    id: Snowflake
    application_id: Snowflake
    guild_id: Snowflake
    permissions: list[ApplicationCommandPermissions]
