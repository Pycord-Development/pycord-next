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

from datetime import datetime
from typing import TYPE_CHECKING

from .application import Application
from .snowflake import Snowflake
from .types import (
    INTEGRATION_EXPIRE_BEHAVIOR,
    INTEGRATION_TYPE,
    SCOPE,
    Account as DiscordAccount,
    Integration as DiscordIntegration,
    IntegrationApplication as DiscordIntegrationApplication,
)
from .undefined import UNDEFINED, UndefinedType
from .user import User

if TYPE_CHECKING:
    from .state import State


class Account:
    def __init__(self, data: DiscordAccount) -> None:
        self.id: str = data['id']
        self.name: str = data['name']


class IntegrationApplication:
    def __init__(self, data: DiscordIntegrationApplication, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.icon: str | None = data['icon']
        self.description: str | None = data['description']
        self.bot: User | UndefinedType = User(data['bot'], state) if data.get('bot') is not None else UNDEFINED


class Integration:
    def __init__(self, data: DiscordIntegration, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.type: INTEGRATION_TYPE = data['type']
        self.enabled: bool | UndefinedType = data.get('enabled', UNDEFINED)
        self.syncing: bool | UndefinedType = data.get('syncing', UNDEFINED)
        self.role_id: Snowflake | UndefinedType = Snowflake(data['role_id']) if data.get('role_id') else UNDEFINED
        self.enable_emoticons: bool | UndefinedType = data.get('enable_emoticons', UNDEFINED)
        self.expire_behavior: INTEGRATION_EXPIRE_BEHAVIOR | UndefinedType = data.get('expire_behavior', UNDEFINED)
        self.expire_grace_period: int | UndefinedType = data.get('expire_grace_period', UNDEFINED)
        self.user: User | UndefinedType = User(data['user'], state) if data.get('user') is not None else UNDEFINED
        self.account: Account = Account(data['account'])
        self.synced_at: UndefinedType | datetime = (
            datetime.fromisoformat(data['synced_at']) if data.get('synced_at') is not None else UNDEFINED
        )
        self.subscriber_count: int | UndefinedType = data.get('subscriber_count', UNDEFINED)
        self.revoked: bool | UndefinedType = data.get('revoked', UNDEFINED)
        self.application: Application | UndefinedType = (
            IntegrationApplication(data['application'], state) if data.get('application') is not None else UNDEFINED
        )
        self.scopes: list[SCOPE] | UndefinedType = data.get('scopes', UNDEFINED)
