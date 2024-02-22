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

from datetime import datetime
from typing import Any, TYPE_CHECKING

from discord_typings._resources._guild import WelcomeChannelData, WelcomeScreenData

from .asset import Asset
from .emoji import Emoji
from .enums import (
    DefaultMessageNotificationLevel, ExplicitContentFilterLevel, MFALevel, NSFWLevel, PremiumTier,
    VerificationLevel,
)
from .flags import MemberFlags, Permissions, SystemChannelFlags, RoleFlags
from .missing import Maybe, MISSING
from .mixins import Identifiable
from .sticker import Sticker
from .user import User

if TYPE_CHECKING:
    from discord_typings import GuildData, PartialGuildData, UnavailableGuildData, GuildFeatures, RoleData, RoleTagsData, GuildMemberData

    from .state import State

__all__ = (
    "Guild",
    "Role",
    "RoleTags",
    "GuildMember",
    "WelcomeScreen",
    "WelcomeScreenChannel",
)


class Guild(Identifiable):
    __slots__ = (
        "_state",
        "_update",
        "id",
        "name",
        "icon_hash",
        "splash_hash",
        "discovery_splash_hash",
        "owner",
        "owner_id",
        "permissions",
        "afk_channel_id",
        "afk_timeout",
        "widget_enabled",
        "widget_channel_id",
        "verification_level",
        "default_message_notifications",
        "explicit_content_filter",
        "roles",
        "emojis",
        "features",
        "mfa_level",
        "application_id",
        "system_channel_id",
        "system_channel_flags",
        "rules_channel_id",
        "max_presences",
        "max_members",
        "vanity_url_code",
        "description",
        "banner_hash",
        "premium_tier",
        "premium_subscription_count",
        "preferred_locale",
        "public_updates_channel_id",
        "max_video_channel_users",
        "max_stage_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "welcome_screen",
        "nsfw_level",
        "stickers",
        "premium_progress_bar_enabled",
        "safety_alerts_channel_id"
    )

    def __init__(self, data: GuildData | PartialGuildData | UnavailableGuildData, state: State) -> None:
        self._state: State = state
        self._update(data)

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return str(self.name)

    def _update(self, data: GuildData | PartialGuildData | UnavailableGuildData) -> None:
        self.id: int = int(data["id"])

        self.name: Maybe[str] = data.get("name", MISSING)
        self.icon_hash: Maybe[str | None] = data.get("icon", MISSING)
        self.splash_hash: Maybe[str | None] = data.get("splash", MISSING)
        self.discovery_splash_hash: Maybe[str | None] = data.get("discovery_splash", MISSING)
        self.owner: Maybe[bool] = data.get("owner", MISSING)
        self.owner_id: Maybe[int] = int(oid) if (oid := data.get("owner_id")) else MISSING
        self.permissions: Maybe[Permissions] = Permissions.from_value(permdata) if (
            permdata := data.get("permissions", MISSING)) else MISSING
        self.afk_channel_id: Maybe[int] = int(afkid) if (afkid := data.get("afk_channel_id")) else MISSING
        self.afk_timeout: Maybe[int] = data.get("afk_timeout", MISSING)
        self.widget_enabled: Maybe[bool] = data.get("widget_enabled", MISSING)
        self.widget_channel_id: Maybe[int] = int(widgetid) if (widgetid := data.get("widget_channel_id")) else MISSING
        self.verification_level: Maybe[VerificationLevel] = VerificationLevel(verlvl) if (
            verlvl := data.get("verification_level")) else MISSING
        self.default_message_notifications: Maybe[DefaultMessageNotificationLevel] = DefaultMessageNotificationLevel(
            dmn
        ) if (dmn := data.get("default_message_notifications")) else MISSING
        self.explicit_content_filter: Maybe[ExplicitContentFilterLevel] = ExplicitContentFilterLevel(ecf) if (
            ecf := data.get("explicit_content_filter")) else MISSING
        self.roles: Maybe[list[Role]] = [Role(role, self._state) for role in roles] if (
            roles := data.get("roles")) else MISSING
        self.emojis: Maybe[list[Emoji]] = [Emoji(emoji, self._state) for emoji in emojis] if (
            emojis := data.get("emojis")) else MISSING
        self.features: Maybe[list[GuildFeatures]] = data.get("features", MISSING)
        self.mfa_level: Maybe[MFALevel] = MFALevel(mfa) if (mfa := data.get("mfa_level")) else MISSING
        self.application_id: int | None = int(appid) if (appid := data.get("application_id")) else None
        self.system_channel_id: int | None = int(sysid) if (sysid := data.get("system_channel_id")) else None
        self.system_channel_flags: Maybe[SystemChannelFlags] = SystemChannelFlags.from_value(sysflags) if (
            sysflags := data.get("system_channel_flags", MISSING)) else MISSING
        self.rules_channel_id: int | None = int(rulesid) if (rulesid := data.get("rules_channel_id")) else None
        self.max_presences: Maybe[int | None] = data.get("max_presences", MISSING)
        self.max_members: Maybe[int | None] = data.get("max_members", MISSING)
        self.vanity_url_code: Maybe[str | None] = data.get("vanity_url_code", MISSING)
        self.description: Maybe[str | None] = data.get("description", MISSING)
        self.banner_hash: Maybe[str | None] = data.get("banner", MISSING)
        self.premium_tier: Maybe[PremiumTier] = PremiumTier(pt) if (pt := data.get("premium_tier")) else MISSING
        self.premium_subscription_count: Maybe[int] = data.get("premium_subscription_count", MISSING)
        self.preferred_locale: Maybe[str] = data.get("preferred_locale", MISSING)
        self.public_updates_channel_id: int | None = int(pubupid) if (
            pubupid := data.get("public_updates_channel_id")) else None
        self.max_video_channel_users: Maybe[int] = data.get("max_video_channel_users", MISSING)
        self.max_stage_video_channel_users: Maybe[int] = data.get("max_stage_video_channel_users", MISSING)
        self.approximate_member_count: Maybe[int] = data.get("approximate_member_count", MISSING)
        self.approximate_presence_count: Maybe[int] = data.get("approximate_presence_count", MISSING)
        self.welcome_screen: Maybe[WelcomeScreen] = WelcomeScreen(wlc) if (
            wlc := data.get("welcome_screen")) else MISSING
        self.nsfw_level: Maybe[NSFWLevel] = NSFWLevel(nsfw) if (nsfw := data.get("nsfw_level")) else MISSING
        self.stickers: Maybe[list[Sticker]] = [Sticker(sticker, self._state) for sticker in stickers] if (
            stickers := data.get("stickers")) else MISSING
        self.premium_progress_bar_enabled: Maybe[bool] = data.get("premium_progress_bar_enabled", MISSING)
        self.safety_alerts_channel_id: int | None = int(safetyid) if (
            safetyid := data.get("safety_alerts_channel_id")) else None

    @property
    def icon(self) -> Asset | None:
        return Asset.from_guild_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None

    @property
    def splash(self) -> Asset | None:
        return Asset.from_guild_splash(self._state, self.id, self.splash_hash) if self.splash_hash else None

    @property
    def discovery_splash(self) -> Asset | None:
        return Asset.from_guild_discovery_splash(
            self._state, self.id, self.discovery_splash_hash
        ) if self.discovery_splash_hash else None

    @property
    def banner(self) -> Asset | None:
        return Asset.from_guild_banner(self._state, self.id, self.banner_hash) if self.banner_hash else None


class Role(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "name",
        "color",
        "hoist",
        "icon_hash",
        "unicode_emoji",
        "position",
        "permissions",
        "managed",
        "mentionable",
        "tags",
        "flags"
    )

    def __init__(self, data: RoleData, state: State) -> None:
        self._state: State = state
        self._update(data)

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return self.name

    def _update(self, data: RoleData) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.color: int = data["color"]
        self.hoist: bool = data["hoist"]
        self.icon_hash: Maybe[str | None] = data.get("icon", MISSING)
        self.unicode_emoji: Maybe[str | None] = data.get("unicode_emoji", MISSING)
        self.position: int = data["position"]
        self.permissions: Permissions = Permissions.from_value(data["permissions"])
        self.managed: bool = data["managed"]
        self.mentionable: bool = data["mentionable"]
        self.tags: Maybe[RoleTags] = RoleTags(roletags) if (roletags := data.get("tags")) else MISSING
        self.flags: RoleFlags = RoleFlags.from_value(data["flags"])

    @property
    def icon(self) -> Asset | None:
        return Asset.from_role_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None


class RoleTags:
    __slots__ = (
        "bot_id",
        "integration_id",
        "premium_subscriber",
        "subscription_listing_id",
        "available_for_purchase",
        "guild_connections"
    )

    def __init__(self, data: RoleTagsData) -> None:
        self.bot_id: Maybe[int] = int(botid) if (botid := data.get("bot_id")) else MISSING
        self.integration_id: Maybe[int] = int(integrationid) if (
            integrationid := data.get("integration_id")) else MISSING
        self.premium_subscriber: bool = "premium_subscriber" in data
        self.subscription_listing_id: Maybe[int] = int(subid) if (
            subid := data.get("subscription_listing_id")) else MISSING
        self.available_for_purchase: bool = "available_for_purchase" in data
        self.guild_connections: bool = "guild_connections" in data


class GuildMember(Identifiable):
    __slots__ = (
        "_state",
        "_user",
        "guild_id",
        "nick",
        "guild_avatar_hash",
        "role_ids",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "pending",
        "permissions",
        "communication_disabled_until"
    )

    def __init__(self, data: GuildMemberData, state: State, guild_id: int = None) -> None:
        self._state: State = state
        self.user: Maybe[User] = User(data["user"], self._state) if "user" in data else MISSING
        self._update(data, guild_id)

    def __repr__(self) -> str:
        return f"<Member user={self.user!r} guild_id={self.guild_id}>"

    def __str__(self) -> str:
        return self.display_name

    def _update(self, data: GuildMemberData, guild_id: int) -> None:
        self.guild_id: int = guild_id
        if "user" in data:
            self.id: int = int(data["user"]["id"])
            if self.user:
                self.user._update(data["user"])
            else:
                self.user: Maybe[User] = User(data["user"], self._state)
        self.nick: Maybe[str | None] = data.get("nick", MISSING)
        self.guild_avatar_hash: Maybe[str | None] = data.get("avatar", MISSING)
        self.role_ids: list[int] = [int(role) for role in data.get("roles", [])]
        self.joined_at: datetime = datetime.fromisoformat(data["joined_at"])
        self.premium_since: Maybe[datetime] = datetime.fromisoformat(ps) if \
            (ps := data.get("premium_since", MISSING)) else ps
        self.deaf: bool = data["deaf"]
        self.mute: bool = data["mute"]
        self.flags: MemberFlags = MemberFlags.from_value(data["flags"])
        self.pending: Maybe[bool] = data.get("pending", MISSING)
        self.permissions: Maybe[Permissions] = Permissions.from_value(perm) \
            if (perm := data.get("permissions", MISSING)) else perm
        self.communication_disabled_until: Maybe[datetime | None] = datetime.fromisoformat(cd) if \
            (cd := data.get("communication_disabled_until", MISSING)) else cd

    @property
    def guild_avatar(self) -> Asset | None:
        return Asset.from_guild_member_avatar(
            self._state, self.guild_id, self._user.id, self.guild_avatar_hash
        ) if self.guild_avatar_hash else None

    @property
    def display_avatar(self) -> Asset | None:
        return self.guild_avatar or self.user.display_avatar

    @property
    def display_name(self) -> str:
        return self.nick or self.user.display_name

    @property
    def mention(self) -> str:
        return self.user.mention


class WelcomeScreen:
    __slots__ = (
        "description",
        "welcome_channels"
    )

    def __init__(self, data: WelcomeScreenData) -> None:
        self.description: str | None = data.get("description")
        self.welcome_channels: list[WelcomeScreenChannel] = [
            WelcomeScreenChannel.from_dict(channel) for channel in data.get("welcome_channels", [])
        ]


class WelcomeScreenChannel:
    __slots__ = (
        "channel_id",
        "description",
        "emoji_id",
        "emoji_name"
    )

    def __init__(self, channel_id: int, description: str, emoji_id: int | None, emoji_name: str | None) -> None:
        self.channel_id: int = channel_id
        self.description: str = description
        self.emoji_id: int | None = emoji_id
        self.emoji_name: str | None = emoji_name

    @classmethod
    def from_dict(cls, data: WelcomeChannelData) -> WelcomeScreenChannel:
        return cls(
            data["channel_id"],
            data["description"],
            data.get("emoji_id"),
            data.get("emoji_name")
        )

    def to_dict(self) -> WelcomeChannelData:
        return {
            "channel_id": self.channel_id,
            "description": self.description,
            "emoji_id": self.emoji_id,
            "emoji_name": self.emoji_name
        }

    def __repr__(self) -> str:
        return (
            f"<WelcomeScreenChannel "
            f"channel_id={self.channel_id} description={self.description} emoji_id={self.emoji_id} "
            f"emoji_name={self.emoji_name}>"
        )
