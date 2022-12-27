# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
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

from typing import TYPE_CHECKING, Any

from .channel import Channel
from .enums import (
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    MFALevel,
    NSFWLevel,
    PremiumTier,
    VerificationLevel,
)
from .flags import Permissions, SystemChannelFlags
from .media import Emoji, Sticker
from .role import Role
from .snowflake import Snowflake
from .types import (
    GUILD_FEATURE,
    LOCALE,
    Ban as DiscordBan,
    Guild as DiscordGuild,
    GuildPreview as DiscordGuildPreview,
    UnavailableGuild,
    Widget as DiscordWidget,
    WidgetSettings as DiscordWidgetSettings,
)
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    from .state import State


class Guild:
    def __init__(self, data: DiscordGuild | UnavailableGuild, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self._state = state
        if not data.get('unavailable'):
            self.unavailable: bool = False
            self.name: str = data['name']
            # TODO: Asset classes
            self._icon: str | None = data['icon']
            self._icon_hash: str | None | UndefinedType = data.get('icon_hash')
            self._splash: str | None = data['splash']
            self._discovery_splash: str | None = data['discovery_splash']
            self.owner: bool | UndefinedType = data.get('owner', UNDEFINED)
            self.owner_id: Snowflake = Snowflake(data.get('owner_id'))
            self.permissions: Permissions = Permissions.from_value(
                data.get('permissions', 0)
            )
            self._afk_channel_id: str | None = data.get('afk_channel_id')
            self.afk_channel_id: Snowflake | None = (
                Snowflake(self._afk_channel_id)
                if self._afk_channel_id is not None
                else None
            )
            self.afk_timeout: int = data.get('afk_timeout')
            self.widget_enabled: bool | UndefinedType = data.get(
                'widget_enabled', UNDEFINED
            )
            self._widget_channel_id: str | None | UndefinedType = data.get(
                'widget_channel_id'
            )
            self.widget_channel_id: UndefinedType | Snowflake | None = (
                Snowflake(self._widget_channel_id)
                if isinstance(self._widget_channel_id, str)
                else self._widget_channel_id
            )
            self.verification_level: VerificationLevel = VerificationLevel(
                data['verification_level']
            )
            self.default_message_notifications: DefaultMessageNotificationLevel = (
                DefaultMessageNotificationLevel(data['default_message_notifications'])
            )
            self.explicit_content_filter: ExplicitContentFilterLevel = (
                ExplicitContentFilterLevel(data['explicit_content_filter'])
            )
            self._roles: list[dict[str, Any]] = data.get('roles', [])
            self._process_roles()
            self._emojis: list[dict[str, Any]] = data.get('emojis', [])
            self._process_emojis()
            self.features: list[GUILD_FEATURE] = data['features']
            self.mfa_level: MFALevel = MFALevel(data['mfa_level'])
            self._application_id: str | None = data.get('application_id')
            self.application_id: Snowflake | None = (
                Snowflake(self._application_id)
                if self._application_id is not None
                else None
            )
            self._system_channel_id: str | None = data.get('system_channel_id')
            self.system_channel_id: Snowflake | None = (
                Snowflake(self._system_channel_id)
                if self._system_channel_id is not None
                else None
            )
            self.system_channel_flags: SystemChannelFlags = (
                SystemChannelFlags.from_value(data['system_channel_flags'])
            )

            self._rules_channel_id: str | None = data.get('rules_channel_id')
            self.rules_channel_id: Snowflake | None = (
                Snowflake(self._rules_channel_id)
                if self._rules_channel_id is not None
                else None
            )
            self.max_presences: int | UndefinedType = data.get(
                'max_presences', UNDEFINED
            )
            self.max_members: int | UndefinedType = data.get('max_members', UNDEFINED)
            self.vanity_url: str | None = data.get('vanity_url_code')
            self.description: str | None = data.get('description')
            self._banner: str | None = data.get('banner')
            self.premium_tier: PremiumTier = PremiumTier(data['premium_tier'])
            self.premium_subscription_count: int | UndefinedType = data.get(
                'premium_subscription_count', UNDEFINED
            )
            self.preferred_locale: LOCALE = data['preferred_locale']
            self._public_updates_channel_id: str | None = data[
                'public_updates_channel_id'
            ]
            self.public_updates_channel_id: Snowflake | None = (
                Snowflake(self._public_updates_channel_id)
                if self._public_updates_channel_id is not None
                else None
            )
            self.max_video_channel_users: int | UndefinedType = data.get(
                'max_video_channel_users', UNDEFINED
            )
            self.approximate_member_count: int | UndefinedType = data.get(
                'approximate_member_count', UNDEFINED
            )
            self.approximate_presence_count: int | UndefinedType = data.get(
                'approximate_presence_count', UNDEFINED
            )
            self._welcome_screen = data.get('welcome_screen', UNDEFINED)
            self.welcome_screen: WelcomeScreen | UndefinedType = (
                WelcomeScreen(self._welcome_screen)
                if self._welcome_screen is not UNDEFINED
                else UNDEFINED
            )
            self.nsfw_level: NSFWLevel = NSFWLevel(data.get('nsfw_level', 0))
            self.stickers: list[Sticker] = [
                Sticker(d, self._state) for d in data.get('stickers', [])
            ]
            self.premium_progress_bar_enabled: bool = data[
                'premium_progress_bar_enabled'
            ]
        else:
            self.unavailable: bool = True

    def _process_roles(self) -> None:
        self.roles: list[Role] = [Role(role, state=self._state) for role in self._roles]

    def _process_emojis(self) -> None:
        self.emojis: list[Emoji] = []
        for emoji in self._emojis:
            emo = Emoji(emoji, state=self._state)
            emo._inject_roles(self.roles)
            self.emojis.append(emo)


class GuildPreview:
    def __init__(self, data: DiscordGuildPreview, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        # TODO: Asset classes
        self._icon: str | None = data['icon']
        self._splash: str | None = data['splash']
        self._discovery_splash: str | None = data['discovery_splash']
        self.emojis: list[Emoji] = [Emoji(emoji, state) for emoji in data['emojis']]
        self.features: list[GUILD_FEATURE] = data['features']
        self.approximate_member_count: int = data['approximate_member_count']
        self.approximate_presence_count: int = data['approximate_presence_count']
        self.description: str | None = data['description']
        self.stickers: list[Sticker] = [
            Sticker(sticker, state) for sticker in data['stickers']
        ]


class WidgetSettings:
    def __init__(self, data: DiscordWidgetSettings) -> None:
        self.enabled: bool = data['enabled']
        self.channel_id: Snowflake | None = (
            Snowflake(data['channel_id']) if data['channel_id'] is not None else None
        )


class Widget:
    def __init__(self, data: DiscordWidget, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.instant_invite: str | None = data['instant_invite']
        self.channels: list[Channel] = [
            Channel(channel, state) for channel in data['channels']
        ]
        self.members: list[User] = [User(user, state) for user in data['members']]


class Ban:
    def __init__(self, data: DiscordBan, state: State) -> None:
        self.user: User = User(data['user'], state)
        self.reason: str | None = data['reason']
