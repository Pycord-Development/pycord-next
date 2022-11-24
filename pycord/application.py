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
from __future__ import annotations

from typing import TYPE_CHECKING

from .flags import ApplicationFlags, Permissions
from .snowflake import Snowflake
from .team import Team
from .types import SCOPE, Application as DiscordApplication, InstallParams as DiscordInstallParams
from .user import User
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class InstallParams:
    def __init__(self, data: DiscordInstallParams) -> None:
        self.scopes: list[SCOPE] = data['scopes']
        self.permissions: Permissions = Permissions._from_value(data['permissions'])


class Application:
    def __init__(self, data: DiscordApplication, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.icon: str | None = data['icon']
        self.description: str = data['description']
        self.rpc_origins: list[str] | UndefinedType = data.get('rpc_origins', UNDEFINED)
        self.bot_public: bool = data['bot_public']
        self.bot_require_code_grant: bool = data['bot_require_code_grant']
        self.terms_of_service_url: str | UndefinedType = data.get('terms_of_service_url', UNDEFINED)
        self.privacy_policy_url: str | UndefinedType = data.get('privacy_policy_url', UNDEFINED)
        self.owner: User | UndefinedType = User(data.get('owner'), state) if data.get('owner') is not None else UNDEFINED
        self.verify_key: str = data.get('verify_key')
        self.team: Team | None = Team(data.get('team')) if data.get('team') is not None else None
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data.get('guild_id')) if data.get('guild_id') is not None else UNDEFINED
        )
        self.primary_sku_id: Snowflake | UndefinedType = (
            Snowflake(data.get('primary_sku_id')) if data.get('primary_sku_id') is not None else UNDEFINED
        )
        self.slug: str | UndefinedType = data.get('slug', UNDEFINED)
        self._cover_image: str | UndefinedType = data.get('cover_image', UNDEFINED)
        self.flags: ApplicationFlags | UndefinedType = (
            ApplicationFlags._from_value(data.get('flags')) if data.get('flags') is not None else UNDEFINED
        )
        self.tags: list[str] | UndefinedType = data.get('tags', UNDEFINED)
        self.install_params: InstallParams | UndefinedType = (
            InstallParams(data.get('install_params')) if data.get('install_params') is not None else UNDEFINED
        )
        self.custom_install_url: str | UndefinedType = data.get('custom_install_url')
