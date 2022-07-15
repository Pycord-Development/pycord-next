# Copyright (c) 2021-2022 VincentRPS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import datetime

from discord_typings import (
    BanData,
    ChannelData,
    ChannelPositionData,
    GuildData,
    GuildMemberData,
    GuildPreviewData,
    GuildWidgetData,
    GuildWidgetSettingsData,
    IntegrationData,
    InviteData,
    ListThreadsData,
    MFALevels,
    PermissionOverwriteData,
    RoleData,
    RolePositionData,
    Snowflake,
    VoiceRegionData,
    WelcomeScreenData
)

from pycord.mixins import RouteCategoryMixin
from pycord.internal.http.route import Route
from pycord.types import ModifyMFALevelData, PrunedData


class GuildRoutes(RouteCategoryMixin):

    # TODO: icon to `Asset`
    async def create_guild(
            self,
            *,
            name: str,
            icon: bytes | None = None,
            verification_level: int | None = None,
            default_message_notifications: int | None = None,
            explicit_content_filter: int | None = None,
            roles: list[RoleData] | None = None,
            channels: list[ChannelData] | None = None,
            afk_channel_id: Snowflake | None = None,
            afk_timeout: int | None = None,
            system_channel_id: Snowflake | None = None,
            system_channel_flags: int | None = None,
    ) -> GuildData:
        payload = {'name': name}
        if icon is not None:
            payload['icon'] = icon
        if verification_level is not None:
            payload['verification_level'] = verification_level
        if default_message_notifications is not None:
            payload['default_message_notifications'] = default_message_notifications
        if explicit_content_filter is not None:
            payload['explicit_content_filter'] = explicit_content_filter
        if roles is not None:
            payload['roles'] = roles
        if channels is not None:
            payload['channels'] = channels
        if afk_channel_id is not None:
            payload['afk_channel_id'] = afk_channel_id
        if afk_timeout is not None:
            payload['afk_timeout'] = afk_timeout
        if system_channel_id is not None:
            payload['system_channel_id'] = system_channel_id
        if system_channel_flags is not None:
            payload['system_channel_flags'] = system_channel_flags
        return await self.request('POST', Route('/guilds'), payload)

    async def get_guild(self, guild_id: Snowflake, with_counts: bool = False) -> GuildData:
        params = {'with_counts': with_counts}
        return await self.request('GET', Route('/guilds/{guild_id}', guild_id=guild_id), params=params)

    async def get_guild_preview(self, guild_id: Snowflake) -> GuildPreviewData:
        return await self.request('GET', Route('/guilds/{guild_id}/preview', guild_id=guild_id), None)

    # TODO: icon, splash, discovery_splash, banner to `Asset`
    async def modify_guild(
            self,
            guild_id: Snowflake,
            *,
            reason: str | None = None,
            name: str | ... = ...,
            verification_level: int | None | ... = ...,
            default_message_notifications: int | None | ... = ...,
            explicit_content_filter: int | None | ... = ...,
            afk_channel_id: Snowflake | None | ... = ...,
            afk_timeout: int | ... = ...,
            icon: bytes | None | ... = ...,
            owner_id: Snowflake | ... = ...,
            splash: bytes | None | ... = ...,
            discovery_splash: bytes | None | ... = ...,
            banner: bytes | None | ... = ...,
            system_channel_id: Snowflake | None | ... = ...,
            system_channel_flags: int | ... = ...,
            rules_channel_id: Snowflake | None | ... = ...,
            public_updates_channel_id: Snowflake | None | ... = ...,
            preferred_locale: str | None | ... = ...,
            features: list[str] | ... = ...,
            description: str | None | ... = ...,
            premium_progress_bar_enabled: bool | ... = ...,
    ) -> GuildData:
        payload = {}
        if name is not ...:
            payload['name'] = name
        if verification_level is not ...:
            payload['verification_level'] = verification_level
        if default_message_notifications is not ...:
            payload['default_message_notifications'] = default_message_notifications
        if explicit_content_filter is not ...:
            payload['explicit_content_filter'] = explicit_content_filter
        if afk_channel_id is not ...:
            payload['afk_channel_id'] = afk_channel_id
        if afk_timeout is not ...:
            payload['afk_timeout'] = afk_timeout
        if icon is not ...:
            payload['icon'] = icon
        if owner_id is not ...:
            payload['owner_id'] = owner_id
        if splash is not ...:
            payload['splash'] = splash
        if discovery_splash is not ...:
            payload['discovery_splash'] = discovery_splash
        if banner is not ...:
            payload['banner'] = banner
        if system_channel_id is not ...:
            payload['system_channel_id'] = system_channel_id
        if system_channel_flags is not ...:
            payload['system_channel_flags'] = system_channel_flags
        if rules_channel_id is not ...:
            payload['rules_channel_id'] = rules_channel_id
        if public_updates_channel_id is not ...:
            payload['public_updates_channel_id'] = public_updates_channel_id
        if preferred_locale is not ...:
            payload['preferred_locale'] = preferred_locale
        if features is not ...:
            payload['features'] = features
        if description is not ...:
            payload['description'] = description
        if premium_progress_bar_enabled is not ...:
            payload['premium_progress_bar_enabled'] = premium_progress_bar_enabled

        return await self.request('PATCH', Route('/guilds/{guild_id}', guild_id=guild_id), payload, reason=reason)

    async def delete_guild(self, guild_id: Snowflake) -> None:
        await self.request('DELETE', Route('/guilds/{guild_id}', guild_id=guild_id), None)

    async def get_guild_channels(self, guild_id: Snowflake) -> list[ChannelData]:
        return await self.request('GET', Route('/guilds/{guild_id}/channels', guild_id=guild_id), None)

    # TODO: type channel_type to ChannelType
    async def create_guild_channel(
            self,
            guild_id: Snowflake,
            name: str,
            *,
            reason: str | None = None,
            channel_type: int | None = None,
            topic: str | None = None,
            bitrate: int | None = None,
            user_limit: int | None = None,
            rate_limit_per_user: int | None = None,
            position: int | None = None,
            permission_overwrites: list[PermissionOverwriteData] | None = None,
            parent_id: Snowflake | None = None,
            nsfw: bool | None = None,
            rtc_region: str | None = None,
            video_quality_mode: int | None = None,
            default_auto_archive_duration: int | None = None,
    ) -> ChannelData:
        payload = {'name': name}
        # TODO: check keys based on channel type?
        if channel_type is not None:
            payload['type'] = channel_type
        if topic is not None:
            payload['topic'] = topic
        if bitrate is not None:
            payload['bitrate'] = bitrate
        if user_limit is not None:
            payload['user_limit'] = user_limit
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user
        if position is not None:
            payload['position'] = position
        if permission_overwrites is not None:
            payload['permission_overwrites'] = permission_overwrites
        if parent_id is not None:
            payload['parent_id'] = parent_id
        if nsfw is not None:
            payload['nsfw'] = nsfw
        if rtc_region is not None:
            payload['rtc_region'] = rtc_region
        if video_quality_mode is not None:
            payload['video_quality_mode'] = video_quality_mode
        if default_auto_archive_duration is not None:
            payload['default_auto_archive_duration'] = default_auto_archive_duration

        return await self.request('POST', Route('/guilds/{guild_id}/channels', guild_id=guild_id), payload,
                                  reason=reason)

    async def modify_guild_channel_positions(
            self,
            guild_id: Snowflake,
            *channel_positions: ChannelPositionData,
    ) -> None:
        payload = list(channel_positions)

        await self.request('PATCH', Route('/guilds/{guild_id}/channels', guild_id=guild_id), payload)

    async def list_active_guild_threads(self, guild_id: Snowflake) -> ListThreadsData:
        return await self.request('GET', Route('/guilds/{guild_id}/threads/active', guild_id=guild_id), None)

    async def get_guild_member(self, guild_id: Snowflake, user_id: Snowflake) -> GuildMemberData:
        return await self.request(
            'GET', Route('/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id), None)

    async def list_guild_members(
            self, guild_id: Snowflake, *, limit: int | None = None, after: Snowflake | None = None
    ) -> list[GuildMemberData]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if after is not None:
            params['after'] = after

        return await self.request('GET', Route('/guilds/{guild_id}/members', guild_id=guild_id), params=params)

    async def search_guild_members(
            self, guild_id: Snowflake, *, query: str, limit: int | None = None
    ) -> list[GuildMemberData]:
        params = {'query': query}
        if limit is not None:
            params['limit'] = limit
        return await self.request('GET', Route('/guilds/{guild_id}/members/search', guild_id=guild_id), params=params)

    async def add_guild_member(
            self,
            guild_id: Snowflake,
            user_id: Snowflake,
            *,
            access_token: str,
            nick: str | None = None,
            roles: list[Snowflake] | None = None,
            mute: bool | None = None,
            deaf: bool | None = None,
    ) -> GuildMemberData:
        payload = {'access_token': access_token}
        if nick is not None:
            payload['nick'] = nick
        if roles is not None:
            payload['roles'] = roles
        if mute is not None:
            payload['mute'] = mute
        if deaf is not None:
            payload['deaf'] = deaf

        return await self.request(
            'PUT', Route('/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id), payload)

    async def modify_guild_member(
            self,
            guild_id: Snowflake,
            user_id: Snowflake,
            *,
            nick: str | None | ... = ...,
            roles: list[Snowflake] | ... = ...,
            mute: bool | ... = ...,
            deaf: bool | ... = ...,
            channel_id: Snowflake | None | ... = ...,
            communication_disabled_until: datetime.datetime | None | ... = ...,
            reason: str | None = None,
    ) -> GuildMemberData:
        payload = {}
        if nick is not ...:
            payload['nick'] = nick
        if roles is not ...:
            payload['roles'] = roles
        if mute is not ...:
            payload['mute'] = mute
        if deaf is not ...:
            payload['deaf'] = deaf
        if channel_id is not ...:
            payload['channel_id'] = channel_id
        if communication_disabled_until is not ...:
            payload['communication_disabled_until'] = communication_disabled_until.isoformat()

        return await self.request(
            'PATCH', Route('/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id),
            payload, reason=reason)

    async def modify_current_member(
            self, guild_id: Snowflake, *, nick: str | None = ..., reason: str | None = None
    ) -> GuildMemberData:
        payload = {}
        if nick is not ...:
            payload['nick'] = nick
        return await self.request(
            'PATCH', Route('/guilds/{guild_id}/members/@me', guild_id=guild_id), payload, reason=reason)

    async def add_guild_member_role(self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake, *,
                                    reason: str | None = None) -> None:
        await self.request(
            'PUT', Route('/guilds/{guild_id}/members/{user_id}/roles/{role_id}', guild_id=guild_id, user_id=user_id,
                         role_id=role_id), None, reason=reason)

    async def remove_guild_member_role(self, guild_id: Snowflake, user_id: Snowflake, role_id: Snowflake, *,
                                       reason: str | None = None) -> None:
        await self.request(
            'DELETE', Route('/guilds/{guild_id}/members/{user_id}/roles/{role_id}', guild_id=guild_id, user_id=user_id,
                            role_id=role_id), None, reason=reason)

    async def remove_guild_member(self, guild_id: Snowflake, user_id: Snowflake, *, reason: str | None = None) -> None:
        await self.request(
            'DELETE',
            Route('/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id), None, reason=reason)

    async def get_guild_bans(
            self,
            guild_id: Snowflake,
            *,
            limit: int | None = None,
            before: Snowflake | None = None,
            after: Snowflake | None = None
    ) -> list[BanData]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        return await self.request('GET', Route('/guilds/{guild_id}/bans', guild_id=guild_id), None)

    async def get_guild_ban(self, guild_id: Snowflake, user_id: Snowflake) -> BanData:
        return await self.request(
            'GET', Route('/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id), None)

    async def create_guild_ban(
            self,
            guild_id: Snowflake,
            user_id: Snowflake,
            *,
            delete_message_days: int | None = None,
            reason: str | None = None
    ) -> None:
        payload = {}
        if delete_message_days is not None:
            payload['delete_message_days'] = delete_message_days
        await self.request(
            'PUT', Route('/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id),
            payload, reason=reason)

    async def remove_guild_ban(self, guild_id: Snowflake, user_id: Snowflake, *, reason: str | None = None) -> None:
        await self.request(
            'DELETE', Route('/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id), None,
            reason=reason)

    async def get_guild_roles(self, guild_id: Snowflake) -> list[RoleData]:
        return await self.request('GET', Route('/guilds/{guild_id}/roles', guild_id=guild_id), None)

    # TODO: icon to `Asset`
    async def create_guild_role(
            self,
            guild_id: Snowflake,
            *,
            name: str | None = None,
            permissions: int | None = None,
            color: int | None = None,
            hoist: bool | None = None,
            icon: bytes | None = None,
            unicode_emoji: str | None = None,
            mentionable: bool | None = None,
            reason: str | None = None
    ) -> RoleData:
        payload = {}
        if name is not None:
            payload['name'] = name
        if permissions is not None:
            payload['permissions'] = permissions
        if color is not None:
            payload['color'] = color
        if hoist is not None:
            payload['hoist'] = hoist
        if icon is not None:
            payload['icon'] = icon
        if unicode_emoji is not None:
            payload['unicode_emoji'] = unicode_emoji
        if mentionable is not None:
            payload['mentionable'] = mentionable

        return await self.request('POST', Route('/guilds/{guild_id}/roles', guild_id=guild_id), payload, reason=reason)

    async def modify_guild_role_positions(
            self,
            guild_id: Snowflake,
            *positions: list[RolePositionData],
            reason: str | None = None
    ) -> None:
        payload = list(positions)
        await self.request(
            'PATCH', Route('/guilds/{guild_id}/roles', guild_id=guild_id), payload, reason=reason)

    async def modify_guild_role(
            self,
            guild_id: Snowflake,
            role_id: Snowflake,
            *,
            name: str | None | ... = ...,
            permissions: int | None | ... = ...,
            color: int | None | ... = ...,
            hoist: bool | None | ... = ...,
            icon: bytes | None | ... = ...,
            unicode_emoji: str | None | ... = ...,
            mentionable: bool | None | ... = ...,
            reason: str | None = None
    ) -> RoleData:
        payload = {}
        if name is not ...:
            payload['name'] = name
        if permissions is not ...:
            payload['permissions'] = permissions
        if color is not ...:
            payload['color'] = color
        if hoist is not ...:
            payload['hoist'] = hoist
        if icon is not ...:
            payload['icon'] = icon
        if unicode_emoji is not ...:
            payload['unicode_emoji'] = unicode_emoji
        if mentionable is not ...:
            payload['mentionable'] = mentionable

        return await self.request(
            'PATCH', Route('/guilds/{guild_id}/roles/{role_id}', guild_id=guild_id, role_id=role_id), payload,
            reason=reason)

    async def modify_guild_mfa_level(self, guild_id: Snowflake, *, level: MFALevels) -> MFALevels:
        payload = {'level': level}

        val: ModifyMFALevelData = await self.request(
            'POST', Route('/guilds/{guild_id}/mfa', guild_id=guild_id), payload)
        return val['level']

    async def delete_guild_role(self, guild_id: Snowflake, role_id: Snowflake, *, reason: str | None = None) -> None:
        await self.request(
            'DELETE', Route('/guilds/{guild_id}/roles/{role_id}', guild_id=guild_id, role_id=role_id), None,
            reason=reason)

    async def get_guild_prune_count(
            self,
            guild_id: Snowflake,
            *,
            days: int | None = None,
            include_roles: list[Snowflake] | None = None,
    ) -> int:
        params = {}
        if days is not None:
            params['days'] = days
        if include_roles is not None:
            params['include_roles'] = ','.join(str(i) for i in include_roles)
        val: PrunedData = await self.request('GET', Route('/guilds/{guild_id}/prune', guild_id=guild_id), params)
        return val['pruned']

    async def begin_guild_prune(
            self,
            guild_id: Snowflake,
            *,
            days: int,
            compute_prune_count: bool,
            include_roles: list[Snowflake] | None = None,
            reason: str | None = None,
    ) -> int | None:
        payload = {
            'days': days,
            'compute_prune_count': compute_prune_count,
            'include_roles': include_roles,
        }

        val: PrunedData = await self.request(
            'POST', Route('/guilds/{guild_id}/prune', guild_id=guild_id), payload, reason=reason)
        return val['pruned']

    async def get_guild_voice_regions(self, guild_id: Snowflake) -> list[VoiceRegionData]:
        return await self.request('GET', Route('/guilds/{guild_id}/regions', guild_id=guild_id), None)

    async def get_guild_invites(self, guild_id: Snowflake) -> list[InviteData]:
        return await self.request('GET', Route('/guilds/{guild_id}/invites', guild_id=guild_id), None)

    async def get_guild_integrations(self, guild_id: Snowflake) -> list[IntegrationData]:
        return await self.request('GET', Route('/guilds/{guild_id}/integrations', guild_id=guild_id), None)

    async def delete_guild_integration(
            self,
            guild_id: Snowflake,
            integration_id: Snowflake,
            *,
            reason: str | None = None
    ) -> None:
        await self.request(
            'DELETE',
            Route('/guilds/{guild_id}/integrations/{integration_id}', guild_id=guild_id, integration_id=integration_id),
            None,
            reason=reason)

    async def get_guild_widget_settings(self, guild_id: Snowflake) -> GuildWidgetSettingsData:
        return await self.request('GET', Route('/guilds/{guild_id}/widget', guild_id=guild_id), None)

    async def modify_guild_widget(
            self,
            guild_id: Snowflake,
            *,
            enabled: bool | ... = ...,
            channel_id: Snowflake | None | ... = ...,
            reason: str | None = None
    ) -> GuildWidgetSettingsData:
        payload = {}
        if enabled is not ...:
            payload['enabled'] = enabled
        if channel_id is not ...:
            payload['channel_id'] = channel_id

        return await self.request(
            'PATCH', Route('/guilds/{guild_id}/widget', guild_id=guild_id), payload, reason=reason)

    async def get_guild_widget(self, guild_id: Snowflake) -> GuildWidgetData:
        return await self.request('GET', Route('/guilds/{guild_id}/widget.json', guild_id=guild_id), None)

    async def get_guild_vanity_url(self, guild_id: Snowflake) -> dict:  # TODO
        return await self.request('GET', Route('/guilds/{guild_id}/vanity-url', guild_id=guild_id), None)

    async def get_guild_widget_image(self, guild_id: Snowflake, *, style: str | None = None) -> bytes:
        params = {}
        if style is not None:
            params['style'] = style

        return await self.request(  # type: ignore
            'GET', Route('/guilds/{guild_id}/widget.png', guild_id=guild_id), params)

    async def get_guild_welcome_screen(self, guild_id: Snowflake) -> WelcomeScreenData:
        return await self.request('GET', Route('/guilds/{guild_id}/welcome-screen', guild_id=guild_id), None)

    async def modify_guild_welcome_screen(
            self,
            guild_id: Snowflake,
            *,
            enabled: bool | ... = ...,
            welcome_channels: list[dict] | None | ... = ...,  # TODO
            description: str | None | ... = ...,
            reason: str | None = None,
    ) -> WelcomeScreenData:
        payload = {}
        if enabled is not ...:
            payload['enabled'] = enabled
        if welcome_channels is not ...:
            payload['welcome_channels'] = welcome_channels
        if description is not ...:
            payload['description'] = description

        return await self.request(
            'PATCH', Route('/guilds/{guild_id}/welcome-screen', guild_id=guild_id), payload, reason=reason)

    async def modify_current_user_voice_state(
            self,
            guild_id: Snowflake,
            *,
            channel_id: Snowflake,
            suppress: bool | ... = ...,
            request_to_speak: datetime.datetime | None | ... = ...,
    ) -> None:
        payload = {'channel_id': channel_id}
        if suppress is not ...:
            payload['suppress'] = suppress
        if request_to_speak is not ...:
            payload['request_to_speak'] = request_to_speak.isoformat()

        await self.request('PATCH', Route('/guilds/{guild_id}/voice-states/@me', guild_id=guild_id), payload)

    async def modify_user_voice_state(
            self,
            guild_id: Snowflake,
            user_id: Snowflake,
            *,
            channel_id: Snowflake,
            suppress: bool | ... = ...,
    ) -> None:
        payload = {'channel_id': channel_id}
        if suppress is not ...:
            payload['suppress'] = suppress

        await self.request(
            'PATCH', Route('/guilds/{guild_id}/voice-states/{user_id}', guild_id=guild_id, user_id=user_id), payload)
