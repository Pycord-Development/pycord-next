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

from .channel import Channel
from .media import Emoji, Sticker
from .role import Role
from .snowflake import Snowflake
from .user import LOCALE, User
from .welcome_screen import WelcomeScreen

VERIFICATION_LEVEL = Literal[0, 1, 2, 3, 4]
DMNLEVEL = Literal[0, 1]
EC_FILTER = Literal[0, 1, 2]
GUILD_FEATURE = Literal[
    'ANIMATED_BANNER',
    'ANIMATED_ICON',
    'AUTO_MODERATION',
    'COMMUNITY',
    'DEVELOPER_SUPPORT_SERVER',
    'DISCOVERABLE',
    'FEATURABLE',
    'INVITES_DISABLED',
    'INVITE_SPLASH',
    'MEMBER_VERIFICATION_GATE_ENABLED',
    'MONETIZATION_ENABLED',
    'MORE_STICKERS',
    'NEWS',
    'PARTNERED',
    'PREVIEW_ENABLED',
    'PRIVATE_THREADS',
    'ROLE_ICONS',
    'TICKETED_EVENTS_ENABLED',
    'VANITY_URL',
    'VERIFIED',
    'VIP_REGIONS',
    'WELCOME_SCREEN_ENABLED',
]
MFA_LEVEL = Literal[0, 1]
PREMIUM_TIER = Literal[0, 1, 2, 3]
NSFW_LEVEL = Literal[0, 1, 2, 3]


class UnavailableGuild(TypedDict):
    id: Snowflake
    unavailable: Literal[True]


class GuildPreview(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    splash: str | None
    discovery_splash: str | None
    emojis: list[Emoji]
    features: list[GUILD_FEATURE]
    approximate_member_count: int
    approximate_presence_count: int
    description: str
    stickers: list[Sticker]


class Guild(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    icon_hash: NotRequired[str | None]
    splash: str | None
    discovery_splash: str | None
    owner: NotRequired[bool]
    owner_id: Snowflake
    permissions: NotRequired[str]
    afk_channel_id: Snowflake | None
    afk_timeout: int
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[Snowflake | None]
    verification_level: VERIFICATION_LEVEL
    default_message_notifications: DMNLEVEL
    explicit_content_filter: EC_FILTER
    roles: list[Role]
    emojis: list[Emoji]
    features: list[GUILD_FEATURE]
    mfa_level: MFA_LEVEL
    application_id: str | None
    system_channel_id: Snowflake | None
    system_channel_flags: int
    rules_channel_id: Snowflake | None
    max_presences: NotRequired[int | None]
    max_members: NotRequired[int]
    vanity_url_code: str | None
    description: str | None
    banner: str | None
    premium_tier: PREMIUM_TIER
    premium_subscription_count: NotRequired[int]
    preferred_locale: LOCALE
    public_updates_channel_id: Snowflake | None
    max_video_channel_users: NotRequired[int]
    approximate_member_count: NotRequired[int]
    approximate_presence_count: NotRequired[int]
    welcome_screen: NotRequired[WelcomeScreen]
    nsfw_level: NSFW_LEVEL
    stickers: NotRequired[list[Sticker]]
    premium_progress_bar_enabled: bool


class WidgetSettings(TypedDict):
    enabled: bool
    channel_id: Snowflake | None


class Widget(TypedDict):
    id: Snowflake
    name: str
    instant_invite: str | None
    channels: list[Channel]
    members: list[User]
    presence_count: int


class GuildMember(TypedDict):
    user: NotRequired[User]
    nick: NotRequired[str | None]
    avatar: NotRequired[str | None]
    roles: list[Snowflake]
    joined_at: str
    premium_since: NotRequired[str | None]
    deaf: bool
    mute: bool
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[str | None]


class Ban(TypedDict):
    reason: str | None
    user: User
