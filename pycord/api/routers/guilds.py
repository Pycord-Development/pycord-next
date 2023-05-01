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

from ...file import File
from ...missing import MISSING, MissingEnum
from ...snowflake import Snowflake
from ...types import (
    MFA_LEVEL,
    WIDGET_STYLE,
    Ban,
    Channel,
    DefaultReaction,
    ForumTag,
    Guild,
    GuildMember,
    GuildPreview,
    Integration,
    Invite,
    ListThreadsResponse,
    ModifyGuildChannelPositionsPayload,
    ModifyGuildRolePositionsPayload,
    PartialInvite,
    Role,
    VoiceRegion,
    WelcomeScreen,
    WelcomeScreenChannel,
    Widget,
    WidgetSettings,
)
from ...utils import remove_undefined, to_datauri
from ..route import Route
from .base import BaseRouter


class Guilds(BaseRouter):
    async def create_guild(
        self,
        *,
        name: str,
        icon: File | MissingEnum = MISSING,
        verification_level: int | MissingEnum = MISSING,
        default_message_notifications: int | MissingEnum = MISSING,
        explicit_content_filter: int | MissingEnum = MISSING,
        roles: list[Role] | MissingEnum = MISSING,
        channels: list[Channel] | MissingEnum = MISSING,
        afk_channel_id: Snowflake | MissingEnum = MISSING,
        afk_timeout: int | MissingEnum = MISSING,
        system_channel_id: Snowflake | MissingEnum = MISSING,
        system_channel_flags: int | MissingEnum = MISSING,
    ) -> Guild:
        payload = {
            'name': name,
            'icon': icon,
            'verification_level': verification_level,
            'default_message_notifications': default_message_notifications,
            'explicit_content_filter': explicit_content_filter,
            'roles': roles,
            'channels': channels,
            'afk_channel_id': afk_channel_id,
            'afk_timeout': afk_timeout,
            'system_channel_id': system_channel_id,
            'system_channel_flags': system_channel_flags,
        }

        if payload.get('icon'):
            payload['icon'] = to_datauri(payload['icon'])

        return await self.request('POST', Route('/guilds'), remove_undefined(**payload))

    async def get_guild(
        self, guild_id: Snowflake, *, with_counts: bool | MissingEnum = MISSING
    ) -> Guild:
        params = {'with_counts': with_counts}
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def get_guild_preview(self, guild_id: Snowflake) -> GuildPreview:
        return await self.request(
            'GET', Route('/guilds/{guild_id}/preview', guild_id=guild_id)
        )

    async def modify_guild(
        self,
        guild_id: Snowflake,
        *,
        name: str | MissingEnum = MISSING,
        verification_level: int | None | MissingEnum = MISSING,
        default_message_notifications: int | None | MissingEnum = MISSING,
        explicit_content_filter: int | None | MissingEnum = MISSING,
        afk_channel_id: Snowflake | None | MissingEnum = MISSING,
        afk_timeout: int | MissingEnum = MISSING,
        icon: File | None | MissingEnum = MISSING,
        owner_id: Snowflake | MissingEnum = MISSING,
        splash: bytes | None | MissingEnum = MISSING,
        discovery_splash: bytes | None | MissingEnum = MISSING,
        banner: File | None | MissingEnum = MISSING,
        system_channel_id: Snowflake | None | MissingEnum = MISSING,
        system_channel_flags: int | MissingEnum = MISSING,
        rules_channel_id: Snowflake | None | MissingEnum = MISSING,
        public_updates_channel_id: Snowflake | None | MissingEnum = MISSING,
        preferred_locale: str | None | MissingEnum = MISSING,
        features: list[str] | MissingEnum = MISSING,
        description: str | None | MissingEnum = MISSING,
        premium_progress_bar_enabled: bool | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Guild:
        payload = {
            'name': name,
            'verification_level': verification_level,
            'default_message_notifications': default_message_notifications,
            'explicit_content_filter': explicit_content_filter,
            'afk_channel_id': afk_channel_id,
            'afk_timeout': afk_timeout,
            'icon': icon,
            'owner_id': owner_id,
            'splash': splash,
            'discovery_splash': discovery_splash,
            'banner': banner,
            'system_channel_id': system_channel_id,
            'system_channel_flags': system_channel_flags,
            'rules_channel_id': rules_channel_id,
            'public_updates_channel_id': public_updates_channel_id,
            'preferred_locale': preferred_locale,
            'features': features,
            'description': description,
            'premium_progress_bar_enabled': premium_progress_bar_enabled,
        }

        if payload.get('icon'):
            payload['icon'] = to_datauri(payload['icon'])
        if payload.get('banner'):
            payload['banner'] = to_datauri(payload['banner'])
        if payload.get('discovery_splash'):
            payload['discovery_splash'] = to_datauri(payload['discovery_splash'])
        if payload.get('splash'):
            payload['splash'] = to_datauri(payload['splash'])

        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def delete_guild(self, guild_id: Snowflake) -> None:
        await self.request('DELETE', Route('/guilds/{guild_id}', guild_id=guild_id))

    async def get_guild_channels(self, guild_id: Snowflake) -> list[Channel]:
        return await self.request(
            'GET', Route('/guilds/{guild_id}/channels', guild_id=guild_id)
        )

    async def create_guild_channel(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        type: int | None | MissingEnum = MISSING,
        topic: str | None | MissingEnum = MISSING,
        bitrate: int | None | MissingEnum = MISSING,
        user_limit: int | None | MissingEnum = MISSING,
        rate_limit_per_user: int | None | MissingEnum = MISSING,
        position: int | None | MissingEnum = MISSING,
        permission_overwrites: list[dict] | None | MissingEnum = MISSING,
        parent_id: Snowflake | None | MissingEnum = MISSING,
        nsfw: bool | None | MissingEnum = MISSING,
        rtc_region: str | None | MissingEnum = MISSING,
        video_quality_mode: int | None | MissingEnum = MISSING,
        default_auto_archive_duration: int | None | MissingEnum = MISSING,
        default_reaction_emoji: DefaultReaction | None | MissingEnum = MISSING,
        available_tags: list[ForumTag] | None | MissingEnum = MISSING,
        default_sort_order: int | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Channel:
        payload = {
            'name': name,
            'type': type,
            'topic': topic,
            'bitrate': bitrate,
            'user_limit': user_limit,
            'rate_limit_per_user': rate_limit_per_user,
            'position': position,
            'permission_overwrites': permission_overwrites,
            'parent_id': parent_id,
            'nsfw': nsfw,
            'rtc_region': rtc_region,
            'video_quality_mode': video_quality_mode,
            'default_auto_archive_duration': default_auto_archive_duration,
            'default_reaction_emoji': default_reaction_emoji,
            'available_tags': available_tags,
            'default_sort_order': default_sort_order,
        }
        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/channels', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_guild_channel_positions(
        self, guild_id: Snowflake, payload: list[ModifyGuildChannelPositionsPayload]
    ) -> None:
        await self.request(
            'PATCH', Route('/guilds/{guild_id}/channels', guild_id=guild_id), payload
        )

    async def list_active_guild_threads(
        self, guild_id: Snowflake
    ) -> list[ListThreadsResponse]:
        return await self.request(
            'GET', Route('/guilds/{guild_id}/threads/active', guild_id=guild_id)
        )

    async def get_guild_member(
        self, guild_id: Snowflake, user_id: Snowflake
    ) -> GuildMember:
        return await self.request(
            'GET',
            Route(
                '/guilds/{guild_id}/members/{user_id}',
                guild_id=guild_id,
                user_id=user_id,
            ),
        )

    async def list_guild_members(
        self,
        guild_id: Snowflake,
        *,
        limit: int | MissingEnum = MISSING,
        after: Snowflake | MissingEnum = MISSING,
    ) -> list[GuildMember]:
        params = {
            'limit': limit,
            'after': str(after) if after is not MISSING else MISSING,
        }
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/members', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def search_guild_members(
        self,
        guild_id: Snowflake,
        *,
        query: str,
        limit: int | None | MissingEnum = MISSING,
    ) -> list[GuildMember]:
        params = {
            'query': query,
            'limit': limit,
        }
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/members/search', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def add_guild_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        access_token: str,
        nick: str | MissingEnum = MISSING,
        roles: list[Snowflake] | MissingEnum = MISSING,
        mute: bool | MissingEnum = MISSING,
        deaf: bool | MissingEnum = MISSING,
    ) -> GuildMember:
        payload = {
            'access_token': access_token,
            'nick': nick,
            'roles': roles,
            'mute': mute,
            'deaf': deaf,
        }
        return await self.request(
            'PUT',
            Route(
                '/guilds/{guild_id}/members/{user_id}',
                guild_id=guild_id,
                user_id=user_id,
            ),
            remove_undefined(**payload),
        )

    async def modify_guild_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        nick: str | None | MissingEnum = MISSING,
        roles: list[Snowflake] | None | MissingEnum = MISSING,
        mute: bool | None | MissingEnum = MISSING,
        deaf: bool | None | MissingEnum = MISSING,
        channel_id: Snowflake | None | MissingEnum = MISSING,
        communication_disabled_until: datetime.datetime | None | MissingEnum = MISSING,
        flags: int | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> GuildMember:
        if communication_disabled_until:
            communication_disabled_until = communication_disabled_until.isoformat()
        payload = {
            'nick': nick,
            'roles': roles,
            'mute': mute,
            'deaf': deaf,
            'channel_id': channel_id,
            'communication_disabled_until': communication_disabled_until,
            'flags': flags,
        }
        return await self.request(
            'PATCH',
            Route(
                '/guilds/{guild_id}/members/{user_id}',
                guild_id=guild_id,
                user_id=user_id,
            ),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_current_member(
        self,
        guild_id: Snowflake,
        *,
        nick: str | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> GuildMember:
        payload = {
            'nick': nick,
        }
        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/members/@me', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def add_guild_member_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'PUT',
            Route(
                '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def remove_guild_member_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def remove_guild_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/members/{user_id}',
                guild_id=guild_id,
                user_id=user_id,
            ),
            reason=reason,
        )

    async def get_guild_bans(
        self,
        guild_id: Snowflake,
        *,
        limit: int | MissingEnum = MISSING,
        before: Snowflake | MissingEnum = MISSING,
        after: Snowflake | MissingEnum = MISSING,
    ) -> list[Ban]:
        params = {
            'limit': limit,
            'before': before,
            'after': after,
        }
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/bans', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def get_guild_ban(self, guild_id: Snowflake, user_id: Snowflake) -> Ban:
        return await self.request(
            'GET',
            Route(
                '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id
            ),
        )

    async def create_guild_ban(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        delete_message_seconds: int | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> None:
        payload = {
            'delete_message_seconds': delete_message_seconds,
        }
        await self.request(
            'PUT',
            Route(
                '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id
            ),
            remove_undefined(**payload),
            reason=reason,
        )

    async def remove_guild_ban(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id
            ),
            reason=reason,
        )

    async def get_guild_roles(self, guild_id: Snowflake) -> list[Role]:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/roles', guild_id=guild_id),
        )

    async def create_guild_role(
        self,
        guild_id: Snowflake,
        *,
        name: str | MissingEnum = MISSING,
        permissions: int | MissingEnum = MISSING,
        color: int | MissingEnum = MISSING,
        hoist: bool | MissingEnum = MISSING,
        icon: bytes | None | MissingEnum = MISSING,  # TODO
        unicode_emoji: str | None | MissingEnum = MISSING,
        mentionable: bool | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Role:
        payload = {
            'name': name,
            'permissions': str(permissions),
            'color': color,
            'hoist': hoist,
            'unicode_emoji': unicode_emoji,
            'mentionable': mentionable,
        }
        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/roles', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_guild_role_positions(
        self,
        guild_id: Snowflake,
        role_positions: list[ModifyGuildRolePositionsPayload],
        *,
        reason: str | None = None,
    ) -> list[Role]:
        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/roles', guild_id=guild_id),
            role_positions,
            reason=reason,
        )

    async def modify_guild_role(
        self,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        name: str | MissingEnum = MISSING,
        permissions: int | MissingEnum = MISSING,
        color: int | MissingEnum = MISSING,
        hoist: bool | MissingEnum = MISSING,
        icon: bytes | None | MissingEnum = MISSING,  # TODO
        unicode_emoji: str | None | MissingEnum = MISSING,
        mentionable: bool | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> Role:
        payload = {
            'name': name,
            'permissions': str(permissions),
            'color': color,
            'hoist': hoist,
            'unicode_emoji': unicode_emoji,
            'mentionable': mentionable,
        }
        return await self.request(
            'PATCH',
            Route(
                '/guilds/{guild_id}/roles/{role_id}', guild_id=guild_id, role_id=role_id
            ),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_guild_mfa_level(
        self,
        guild_id: Snowflake,
        level: MFA_LEVEL,
        *,
        reason: str | None = None,
    ) -> MFA_LEVEL:
        payload = {
            'level': level,
        }
        response = await self.request(
            'PATCH',
            Route('/guilds/{guild_id}', guild_id=guild_id),
            payload,
            reason=reason,
        )
        return response['level']

    async def delete_guild_role(
        self,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/roles/{role_id}', guild_id=guild_id, role_id=role_id
            ),
            reason=reason,
        )

    async def get_guild_prune_count(
        self,
        guild_id: Snowflake,
        *,
        days: int | MissingEnum = MISSING,
        include_roles: list[Snowflake] | MissingEnum = MISSING,
    ) -> int:
        params = {
            'days': days,
            'include_roles': include_roles,
        }
        response = await self.request(
            'GET',
            Route('/guilds/{guild_id}/prune', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )
        return response['pruned']

    async def begin_guild_prune(
        self,
        guild_id: Snowflake,
        *,
        days: int | MissingEnum = MISSING,
        compute_prune_count: bool | MissingEnum = MISSING,
        include_roles: list[Snowflake] | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> int:
        payload = {
            'days': days,
            'compute_prune_count': compute_prune_count,
            'include_roles': include_roles,
        }
        response = await self.request(
            'POST',
            Route('/guilds/{guild_id}/prune', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )
        return response['pruned']

    async def get_guild_voice_regions(self, guild_id: Snowflake) -> list[VoiceRegion]:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/regions', guild_id=guild_id),
        )

    async def get_guild_invites(self, guild_id: Snowflake) -> list[Invite]:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/invites', guild_id=guild_id),
        )

    async def get_guild_integrations(self, guild_id: Snowflake) -> list[Integration]:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/integrations', guild_id=guild_id),
        )

    async def delete_guild_integration(
        self,
        guild_id: Snowflake,
        integration_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/integrations/{integration_id}',
                guild_id=guild_id,
                integration_id=integration_id,
            ),
            reason=reason,
        )

    async def get_guild_widget_settings(self, guild_id: Snowflake) -> WidgetSettings:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/widget', guild_id=guild_id),
        )

    async def modify_guild_widget(
        self,
        guild_id: Snowflake,
        *,
        enabled: bool | MissingEnum = MISSING,
        channel_id: Snowflake | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> WidgetSettings:
        payload = {
            'enabled': enabled,
            'channel_id': channel_id,
        }
        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/widget', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def get_guild_widget(self, guild_id: Snowflake) -> Widget:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/widget.json', guild_id=guild_id),
        )

    async def get_guild_vanity_url(self, guild_id: Snowflake) -> PartialInvite:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/vanity-url', guild_id=guild_id),
        )

    async def get_guild_widget_image(
        self, guild_id: Snowflake, style: WIDGET_STYLE | MissingEnum = MISSING
    ) -> bytes:
        params = {
            'style': style,
        }
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/widget.png', guild_id=guild_id),
            query_params=remove_undefined(**params),
        )

    async def get_guild_welcome_screen(self, guild_id: Snowflake) -> WelcomeScreen:
        return await self.request(
            'GET',
            Route('/guilds/{guild_id}/welcome-screen', guild_id=guild_id),
        )

    async def modify_guild_welcome_screen(
        self,
        guild_id: Snowflake,
        *,
        enabled: bool | None | MissingEnum = MISSING,
        welcome_channels: list[WelcomeScreenChannel] | None | MissingEnum = MISSING,
        description: str | None | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> WelcomeScreen:
        payload = {
            'enabled': enabled,
            'welcome_channels': welcome_channels,
            'description': description,
        }
        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/welcome-screen', guild_id=guild_id),
            remove_undefined(**payload),
            reason=reason,
        )

    async def modify_current_user_voice_state(
        self,
        guild_id: Snowflake,
        *,
        channel_id: Snowflake | MissingEnum = MISSING,
        suppress: bool | MissingEnum = MISSING,
        request_to_speak_timestamp: datetime.datetime | None | MissingEnum = MISSING,
    ) -> None:
        if request_to_speak_timestamp:
            request_to_speak_timestamp = request_to_speak_timestamp.isoformat()
        payload = {
            'channel_id': channel_id,
            'suppress': suppress,
            'request_to_speak_timestamp': request_to_speak_timestamp,
        }
        await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/voice-states/@me', guild_id=guild_id),
            remove_undefined(**payload),
        )

    async def modify_user_voice_state(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        channel_id: Snowflake | MissingEnum = MISSING,
        suppress: bool | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> None:
        payload = {
            'channel_id': channel_id,
            'suppress': suppress,
        }
        await self.request(
            'PATCH',
            Route(
                '/guilds/{guild_id}/voice-states/{user_id}',
                guild_id=guild_id,
                user_id=user_id,
            ),
            remove_undefined(**payload),
            reason=reason,
        )
