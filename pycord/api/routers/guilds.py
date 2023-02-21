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
import datetime

from .base import BaseRouter
from ..route import Route
from ...snowflake import Snowflake
from ...types import (
    Ban, Channel, DefaultReaction, ForumTag, Guild, GuildPreview, Integration, Invite, ListThreadsResponse,
    MFA_LEVEL, ModifyGuildChannelPositionsPayload,
    ModifyGuildRolePositionsPayload, PartialInvite, Role, GuildMember, VoiceRegion, WelcomeScreen, WelcomeScreenChannel,
    Widget, WIDGET_STYLE,
    WidgetSettings,
)
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined


class Guilds(BaseRouter):
    async def create_guild(
        self, *,
        name: str,
        icon: bytes | UndefinedType = UNDEFINED,  # TODO
        verification_level: int | UndefinedType = UNDEFINED,
        default_message_notifications: int | UndefinedType = UNDEFINED,
        explicit_content_filter: int | UndefinedType = UNDEFINED,
        roles: list[Role] | UndefinedType = UNDEFINED,
        channels: list[Channel] | UndefinedType = UNDEFINED,
        afk_channel_id: Snowflake | UndefinedType = UNDEFINED,
        afk_timeout: int | UndefinedType = UNDEFINED,
        system_channel_id: Snowflake | UndefinedType = UNDEFINED,
        system_channel_flags: int | UndefinedType = UNDEFINED,
    ) -> Guild:
        payload = {
            "name": name,
            "icon": icon,
            "verification_level": verification_level,
            "default_message_notifications": default_message_notifications,
            "explicit_content_filter": explicit_content_filter,
            "roles": roles,
            "channels": channels,
            "afk_channel_id": afk_channel_id,
            "afk_timeout": afk_timeout,
            "system_channel_id": system_channel_id,
            "system_channel_flags": system_channel_flags,
        }
        return await self.request(
            "POST",
            Route("/guilds"),
            remove_undefined(**payload)
        )

    async def get_guild(
        self, guild_id: Snowflake, *,
        with_counts: bool | UndefinedType = UNDEFINED
    ) -> Guild:
        params = {
            "with_counts": with_counts
        }
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}", guild_id=guild_id),
            query_params=remove_undefined(**params)
        )

    async def get_guild_preview(self, guild_id: Snowflake) -> GuildPreview:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/preview", guild_id=guild_id)
        )

    async def modify_guild(
        self, guild_id: Snowflake, *,
        name: str | UndefinedType = UNDEFINED,
        verification_level: int | None | UndefinedType = UNDEFINED,
        default_message_notifications: int | None | UndefinedType = UNDEFINED,
        explicit_content_filter: int | None | UndefinedType = UNDEFINED,
        afk_channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        afk_timeout: int | UndefinedType = UNDEFINED,
        icon: bytes | None | UndefinedType = UNDEFINED,  # TODO
        owner_id: Snowflake | UndefinedType = UNDEFINED,
        splash: bytes | None | UndefinedType = UNDEFINED,  # TODO
        discovery_splash: bytes | None | UndefinedType = UNDEFINED,  # TODO
        banner: bytes | None | UndefinedType = UNDEFINED,  # TODO
        system_channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        system_channel_flags: int | UndefinedType = UNDEFINED,
        rules_channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        public_updates_channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        preferred_locale: str | None | UndefinedType = UNDEFINED,
        features: list[str] | UndefinedType = UNDEFINED,
        description: str | None | UndefinedType = UNDEFINED,
        premium_progress_bar_enabled: bool | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Guild:
        payload = {
            "name": name,
            "verification_level": verification_level,
            "default_message_notifications": default_message_notifications,
            "explicit_content_filter": explicit_content_filter,
            "afk_channel_id": afk_channel_id,
            "afk_timeout": afk_timeout,
            "icon": icon,
            "owner_id": owner_id,
            "splash": splash,
            "discovery_splash": discovery_splash,
            "banner": banner,
            "system_channel_id": system_channel_id,
            "system_channel_flags": system_channel_flags,
            "rules_channel_id": rules_channel_id,
            "public_updates_channel_id": public_updates_channel_id,
            "preferred_locale": preferred_locale,
            "features": features,
            "description": description,
            "premium_progress_bar_enabled": premium_progress_bar_enabled,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def delete_guild(self, guild_id: Snowflake) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}", guild_id=guild_id)
        )

    async def get_guild_channels(self, guild_id: Snowflake) -> list[Channel]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/channels", guild_id=guild_id)
        )

    async def create_guild_channel(
        self, guild_id: Snowflake, *,
        name: str,
        type: int | None | UndefinedType = UNDEFINED,
        topic: str | None | UndefinedType = UNDEFINED,
        bitrate: int | None | UndefinedType = UNDEFINED,
        user_limit: int | None | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[dict] | None | UndefinedType = UNDEFINED,
        parent_id: Snowflake | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: int | None | UndefinedType = UNDEFINED,
        default_auto_archive_duration: int | None | UndefinedType = UNDEFINED,
        default_reaction_emoji: DefaultReaction | None | UndefinedType = UNDEFINED,
        available_tags: list[ForumTag] | None | UndefinedType = UNDEFINED,
        default_sort_order: int | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Channel:
        payload = {
            "name": name,
            "type": type,
            "topic": topic,
            "bitrate": bitrate,
            "user_limit": user_limit,
            "rate_limit_per_user": rate_limit_per_user,
            "position": position,
            "permission_overwrites": permission_overwrites,
            "parent_id": parent_id,
            "nsfw": nsfw,
            "rtc_region": rtc_region,
            "video_quality_mode": video_quality_mode,
            "default_auto_archive_duration": default_auto_archive_duration,
            "default_reaction_emoji": default_reaction_emoji,
            "available_tags": available_tags,
            "default_sort_order": default_sort_order,
        }
        return await self.request(
            "POST",
            Route("/guilds/{guild_id}/channels", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def modify_guild_channel_positions(
        self, guild_id: Snowflake, payload: list[ModifyGuildChannelPositionsPayload]
    ) -> None:
        await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/channels", guild_id=guild_id),
            payload
        )

    async def list_active_guild_threads(self, guild_id: Snowflake) -> list[ListThreadsResponse]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/threads/active", guild_id=guild_id)
        )

    async def get_guild_member(self, guild_id: Snowflake, user_id: Snowflake) -> GuildMember:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)
        )

    async def list_guild_members(
        self, guild_id: Snowflake, *,
        limit: int | UndefinedType = UNDEFINED,
        after: Snowflake | UndefinedType = UNDEFINED,
    ) -> list[GuildMember]:
        params = {
            "limit": limit,
            "after": str(after) if after is not UNDEFINED else UNDEFINED,
        }
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/members", guild_id=guild_id),
            query_params=remove_undefined(**params)
        )

    async def search_guild_members(
        self, guild_id: Snowflake, *,
        query: str,
        limit: int | None | UndefinedType = UNDEFINED,
    ) -> list[GuildMember]:
        params = {
            "query": query,
            "limit": limit,
        }
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/members/search", guild_id=guild_id),
            query_params=remove_undefined(**params)
        )

    async def add_guild_member(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        access_token: str,
        nick: str | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | UndefinedType = UNDEFINED,
        mute: bool | UndefinedType = UNDEFINED,
        deaf: bool | UndefinedType = UNDEFINED,
    ) -> GuildMember:
        payload = {
            "access_token": access_token,
            "nick": nick,
            "roles": roles,
            "mute": mute,
            "deaf": deaf,
        }
        return await self.request(
            "PUT",
            Route("/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id),
            remove_undefined(**payload)
        )

    async def modify_guild_member(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        nick: str | None | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | None | UndefinedType = UNDEFINED,
        mute: bool | None | UndefinedType = UNDEFINED,
        deaf: bool | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        communication_disabled_until: datetime.datetime | None | UndefinedType = UNDEFINED,
        flags: int | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> GuildMember:
        if communication_disabled_until:
            communication_disabled_until = communication_disabled_until.isoformat()
        payload = {
            "nick": nick,
            "roles": roles,
            "mute": mute,
            "deaf": deaf,
            "channel_id": channel_id,
            "communication_disabled_until": communication_disabled_until,
            "flags": flags,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def modify_current_member(
        self, guild_id: Snowflake, *,
        nick: str | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> GuildMember:
        payload = {
            "nick": nick,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/members/@me", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def add_guild_member_role(
        self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "PUT",
            Route("/guilds/{guild_id}/members/{user_id}/roles/{role_id}", guild_id=guild_id, user_id=user_id, role_id=role_id),
            reason=reason
        )

    async def remove_guild_member_role(
        self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}/members/{user_id}/roles/{role_id}", guild_id=guild_id, user_id=user_id, role_id=role_id),
            reason=reason
        )

    async def remove_guild_member(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id),
            reason=reason
        )

    async def get_guild_bans(
        self, guild_id: Snowflake, *,
        limit: int | UndefinedType = UNDEFINED,
        before: Snowflake | UndefinedType = UNDEFINED,
        after: Snowflake | UndefinedType = UNDEFINED,
    ) -> list[Ban]:
        params = {
            "limit": limit,
            "before": before,
            "after": after,
        }
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/bans", guild_id=guild_id),
            query_params=remove_undefined(**params)
        )

    async def get_guild_ban(
        self, guild_id: Snowflake, user_id: Snowflake
    ) -> Ban:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id),
        )

    async def create_guild_ban(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        delete_message_seconds: int | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> None:
        payload = {
            "delete_message_seconds": delete_message_seconds,
        }
        await self.request(
            "PUT",
            Route("/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def remove_guild_ban(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id),
            reason=reason
        )

    async def get_guild_roles(self, guild_id: Snowflake) -> list[Role]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/roles", guild_id=guild_id),
        )

    async def create_guild_role(
        self, guild_id: Snowflake, *,
        name: str | UndefinedType = UNDEFINED,
        permissions: int | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: bytes | None | UndefinedType = UNDEFINED,  # TODO
        unicode_emoji: str | None | UndefinedType = UNDEFINED,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Role:
        payload = {
            "name": name,
            "permissions": str(permissions),
            "color": color,
            "hoist": hoist,
            "unicode_emoji": unicode_emoji,
            "mentionable": mentionable,
        }
        return await self.request(
            "POST",
            Route("/guilds/{guild_id}/roles", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def modify_guild_role_positions(
        self, guild_id: Snowflake, role_positions: list[ModifyGuildRolePositionsPayload], *,
        reason: str | None = None,
    ) -> list[Role]:
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/roles", guild_id=guild_id),
            role_positions,
            reason=reason
        )

    async def modify_guild_role(
        self, guild_id: Snowflake, role_id: Snowflake, *,
        name: str | UndefinedType = UNDEFINED,
        permissions: int | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: bytes | None | UndefinedType = UNDEFINED,  # TODO
        unicode_emoji: str | None | UndefinedType = UNDEFINED,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Role:
        payload = {
            "name": name,
            "permissions": str(permissions),
            "color": color,
            "hoist": hoist,
            "unicode_emoji": unicode_emoji,
            "mentionable": mentionable,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def modify_guild_mfa_level(
        self, guild_id: Snowflake, level: MFA_LEVEL, *,
        reason: str | None = None,
    ) -> MFA_LEVEL:
        payload = {
            "level": level,
        }
        response = await self.request(
            "PATCH",
            Route("/guilds/{guild_id}", guild_id=guild_id),
            payload,
            reason=reason
        )
        return response["level"]

    async def delete_guild_role(
        self, guild_id: Snowflake, role_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id),
            reason=reason
        )

    async def get_guild_prune_count(
        self, guild_id: Snowflake, *,
        days: int | UndefinedType = UNDEFINED,
        include_roles: list[Snowflake] | UndefinedType = UNDEFINED,
    ) -> int:
        params = {
            "days": days,
            "include_roles": include_roles,
        }
        response = await self.request(
            "GET",
            Route("/guilds/{guild_id}/prune", guild_id=guild_id),
            query_params=remove_undefined(**params)
        )
        return response["pruned"]

    async def begin_guild_prune(
        self, guild_id: Snowflake, *,
        days: int | UndefinedType = UNDEFINED,
        compute_prune_count: bool | UndefinedType = UNDEFINED,
        include_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> int:
        payload = {
            "days": days,
            "compute_prune_count": compute_prune_count,
            "include_roles": include_roles,
        }
        response = await self.request(
            "POST",
            Route("/guilds/{guild_id}/prune", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )
        return response["pruned"]

    async def get_guild_voice_regions(self, guild_id: Snowflake) -> list[VoiceRegion]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/regions", guild_id=guild_id),
        )

    async def get_guild_invites(self, guild_id: Snowflake) -> list[Invite]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/invites", guild_id=guild_id),
        )

    async def get_guild_integrations(self, guild_id: Snowflake) -> list[Integration]:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/integrations", guild_id=guild_id),
        )

    async def delete_guild_integration(
        self, guild_id: Snowflake, integration_id: Snowflake, *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            "DELETE",
            Route("/guilds/{guild_id}/integrations/{integration_id}", guild_id=guild_id, integration_id=integration_id),
            reason=reason
        )

    async def get_guild_widget_settings(self, guild_id: Snowflake) -> WidgetSettings:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/widget", guild_id=guild_id),
        )

    async def modify_guild_widget(
        self, guild_id: Snowflake, *,
        enabled: bool | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> WidgetSettings:
        payload = {
            "enabled": enabled,
            "channel_id": channel_id,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/widget", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason
        )

    async def get_guild_widget(self, guild_id: Snowflake) -> Widget:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/widget.json", guild_id=guild_id),
        )

    async def get_guild_vanity_url(self, guild_id: Snowflake) -> PartialInvite:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/vanity-url", guild_id=guild_id),
        )

    async def get_guild_widget_image(
        self,
        guild_id: Snowflake,
        style: WIDGET_STYLE | UndefinedType = UNDEFINED
    ) -> bytes:
        params = {
            "style": style,
        }
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/widget.png", guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def get_guild_welcome_screen(self, guild_id: Snowflake) -> WelcomeScreen:
        return await self.request(
            "GET",
            Route("/guilds/{guild_id}/welcome-screen", guild_id=guild_id),
        )

    async def modify_guild_welcome_screen(
        self, guild_id: Snowflake, *,
        enabled: bool | None | UndefinedType = UNDEFINED,
        welcome_channels: list[WelcomeScreenChannel] | None | UndefinedType = UNDEFINED,
        description: str | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> WelcomeScreen:
        payload = {
            "enabled": enabled,
            "welcome_channels": welcome_channels,
            "description": description,
        }
        return await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/welcome-screen", guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_current_user_voice_state(
        self, guild_id: Snowflake, *,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        suppress: bool | UndefinedType = UNDEFINED,
        request_to_speak_timestamp: datetime.datetime | None | UndefinedType = UNDEFINED,
    ) -> None:
        if request_to_speak_timestamp:
            request_to_speak_timestamp = request_to_speak_timestamp.isoformat()
        payload = {
            "channel_id": channel_id,
            "suppress": suppress,
            "request_to_speak_timestamp": request_to_speak_timestamp,
        }
        await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/voice-states/@me", guild_id=guild_id),
            remove_undefined(**payload),
        )

    async def modify_user_voice_state(
        self, guild_id: Snowflake, user_id: Snowflake, *,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        suppress: bool | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> None:
        payload = {
            "channel_id": channel_id,
            "suppress": suppress,
        }
        await self.request(
            "PATCH",
            Route("/guilds/{guild_id}/voice-states/{user_id}", guild_id=guild_id, user_id=user_id),
            remove_undefined(**payload),
            reason=reason,
        )
