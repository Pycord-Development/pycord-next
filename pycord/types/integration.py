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

from .snowflake import Snowflake
from .user import User

SCOPE = Literal[
    'activities.read',
    'activities.write',
    'applications.builds.read',
    'applications.builds.upload',
    'applications.commands',
    'applications.commands.update',
    'applications.commands.permissions.update',
    'applications.entitlements',
    'applications.store.update',
    'bot',
    'connections',
    'dm_channels.read',
    'email',
    'guilds',
    'guilds.join',
    'guilds.members.read',
    'identify',
    'messages.send',
    'relationships.read',
    'rpc',
    'rpc.activities.write',
    'rpc.notifications.read',
    'rpc.voice.read',
    'rpc.voice.write',
    'voice',
    'webhook.incoming',
]


class Account(TypedDict):
    id: str
    name: str


class IntegrationApplication(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str
    bot: NotRequired[User]


class Integration(TypedDict):
    id: Snowflake
    name: str
    type: Literal['twitch', 'youtube', 'discord']
    enabled: NotRequired[bool]
    syncing: NotRequired[bool]
    role_id: NotRequired[Snowflake]
    enabled_emoticons: NotRequired[bool]
    expire_behavior: NotRequired[Literal[0, 1]]
    expire_grace_period: NotRequired[int]
    user: NotRequired[User]
    account: Account
    synced_at: NotRequired[str]
    subscriber_count: NotRequired[int]
    revoked: NotRequired[bool]
    application: NotRequired[IntegrationApplication]
    scopes: list[SCOPE]
