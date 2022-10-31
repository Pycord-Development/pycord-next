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

from .integration import SCOPE
from .snowflake import Snowflake
from .user import User


class TeamMember(TypedDict):
    membership_state: Literal[1, 2]
    permissions: list[str]
    team_id: Snowflake
    user: User


class Team(TypedDict):
    icon: str | None
    id: Snowflake
    members: list[TeamMember]
    name: str
    owner_user_id: Snowflake


class InstallParams(TypedDict):
    scopes: list[SCOPE]
    permissions: str


class Application(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str
    rpc_origins: NotRequired[list[str]]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    owner: NotRequired[User]
    summary: NotRequired[str]
    verify_key: str
    team: Team | None
    guild_id: NotRequired[Snowflake]
    privacy_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    cover_image: NotRequired[str]
    flags: NotRequired[int]
    tags: NotRequired[list[str]]
    install_params: InstallParams
    custom_install_url: NotRequired[str]
