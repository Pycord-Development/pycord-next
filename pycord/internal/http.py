# MIT License
#
# Copyright (c) 2023 Pycord
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
# SOFTWARE.

import logging
import sys
from datetime import datetime
from typing import Any, cast, Literal, Type, TYPE_CHECKING, TypeVar

import aiohttp
from aiohttp import __version__ as aiohttp_version, BasicAuth, ClientSession, FormData
from discord_typings import (
    AllowedMentionsData, ApplicationCommandData, ApplicationCommandOptionData, ApplicationCommandPermissionsData,
    ApplicationCommandTypes, ApplicationData, ApplicationRoleConnectionData, ApplicationRoleConnectionMetadataData,
    AuditLogData, AuditLogEvents, AutoModerationActionData, AutoModerationEventTypes, AutoModerationRuleData,
    AutoModerationTriggerMetadataData, AutoModerationTriggerTypes, BanData, ChannelData, ChannelTypes, ComponentData,
    ConnectionData, DefaultMessageNotificationLevels, DefaultReactionData, EmbedData, EmojiData,
    ExplicitContentFilterLevels, FollowedChannelData, ForumLayoutTypes, ForumTagData, GetGatewayBotData,
    GuildApplicationCommandPermissionData, GuildData, GuildFeatures, GuildMemberData, GuildOnboardingData,
    GuildOnboardingModes, GuildOnboardingPromptsData, GuildPreviewData, GuildScheduledEventData,
    GuildScheduledEventEntityMetadataData, GuildScheduledEventEntityTypes, GuildScheduledEventPrivacyLevels,
    GuildScheduledEventStatus, GuildScheduledEventUserData, GuildTemplateData, GuildWidgetData, GuildWidgetSettingsData,
    HasMoreListThreadsData, InstallParams, IntegrationData, InviteData, MessageData, MessageReferenceData, MFALevels,
    PartialAttachmentData, PartialGuildData, PermissionOverwriteData, RoleData, SortOrderTypes, StageInstanceData,
    StageInstancePrivacyLevels, StickerData, StickerPackData, ThreadMemberData, UserData, VerificationLevels,
    VoiceRegionData, WebhookData, WelcomeChannelData, WelcomeScreenData,
)
from msgspec import json

from .._about import __version__
from ..errors import BotException, DiscordException, Forbidden, HTTPException, NotFound
from ..file import File
from ..missing import Maybe, MISSING, MissingEnum
from ..types.channel import (
    ChannelPositionUpdateData, ForumThreadMessageParams,
)
from ..types.guild import (
    MFALevelResponse,
    PruneCountResponse,
    RolePositionUpdateData, VanityURLData,
)
from ..utils import form_qs, remove_undefined, to_datauri

_log = logging.getLogger(__name__)

T = TypeVar("T")


class Route:
    def __init__(
        self,
        client: "HTTPClient",
        path: str,
        guild_id: int | None = None,
        channel_id: int | None = None,
        webhook_id: int | None = None,
        webhook_token: str | None = None,
        **parameters: object,
    ) -> None:
        self.client = client  # TODO: why?
        self.path: str = path.format(**parameters)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.webhook_id = webhook_id
        self.webhook_token = webhook_token
        self.parameters = parameters

    @property
    def bucket(self) -> str:
        return f"{self.path}:{self.guild_id}:{self.channel_id}:{self.webhook_id}:{self.webhook_token}"


class HTTPClient:
    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://discord.com/api/v10",
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.base_url = base_url
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._headers = {
            "User-Agent": "DiscordBot (https://pycord.dev, {0}) Python/{1[0]}.{1[1]} aiohttp/{2}".format(
                __version__, sys.version_info, aiohttp_version
            ),
        }
        if token:
            self._headers["Authorization"] = f"Bot {token}"

        self._session: None | ClientSession = None

    async def force_start(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def request(  # type: ignore[return]
        self,
        method: str,
        route: Route,
        data: dict[str, Any] | list[Any] | None = None,
        files: list[File] | None = None,
        add_files: bool = True,
        form: list[dict[str, Any]] | None = None,
        *,
        reason: str | None = None,
        query_params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        t: Type[T],
    ) -> T:
        endpoint = self.base_url + route.path

        if self._session is None:
            self._session = aiohttp.ClientSession()

        if TYPE_CHECKING:
            assert self._session

        _headers = self._headers.copy()
        if headers:
            _headers.update(headers)

        if reason:
            headers["X-Audit-Log-Reason"] = reason

        payload: bytes | FormData

        if data:
            data = json.encode(data)
            headers.update({"Content-Type": "application/json"})

        if form and data:
            form.append({"name": "payload_json", "value": data})

        if files and add_files:
            if not form:
                form = []

            for idx, file in enumerate(files):
                form.append(
                    {
                        "name": f"files[{idx}]",
                        "value": file.file.read(),
                        "filename": file.filename,
                        "content_type": "application/octet-stream",
                    }
                )

        _log.debug(f"Requesting to {endpoint} with {data}, {headers}")

        for try_ in range(5):
            if files:
                for file in files:
                    file.reset(try_)

            if form:
                payload = FormData(quote_fields=False)
                for params in form:
                    payload.add_field(**params)

            r = await self._session.request(
                method,
                endpoint,
                data=data,
                headers=_headers,
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
                params=query_params,
            )
            _log.debug(f"Received back {await r.text()}")

            if t:
                d = cast(T, json.decode(await r.read()))
            else:
                d = cast(T, await r.text())

            if r.status == 429:
                # TODO: properly handle rate limits
                _log.debug(f"Request to {endpoint} failed: Request returned rate limit")
                raise HTTPException(r, d, data)

            elif r.status == 403:
                raise Forbidden(r, d, data)
            elif r.status == 404:
                raise NotFound(r, d, data)
            elif r.status == 500:
                raise DiscordException(r, d, data)
            elif r.ok:
                return d
            else:
                raise HTTPException(r, d, data)

    # cdn
    async def get_from_cdn(self, url: str) -> bytes:
        if self._session is None:
            self._session = aiohttp.ClientSession()

        if TYPE_CHECKING:
            assert self._session

        r = await self._session.request(
            "GET",
            url,
        )
        d = await r.read()
        if r.status == 403:
            raise Forbidden(r, d, None)
        elif r.status == 404:
            raise NotFound(r, d, None)
        elif r.status == 500:
            raise DiscordException(r, d, None)
        elif r.ok:
            return d
        else:
            raise HTTPException(r, d, None)

    # Application
    async def get_current_application(self) -> ApplicationData:
        return cast(
            ApplicationData,
            await self.request(
                'GET', Route(self, '/oauth2/applications/@me'), t=ApplicationData,
            )
        )

    async def edit_current_application(
        self,
        custom_install_url: Maybe[str] = MISSING,
        description: Maybe[str] = MISSING,
        role_connections_verification_url: Maybe[str] = MISSING,
        install_params: Maybe[InstallParams] = MISSING,
        flags: Maybe[int] = MISSING,
        icon: Maybe[File | None] = MISSING,
        cover_image: Maybe[File | None] = MISSING,
        interactions_endpoint_url: Maybe[str] = MISSING,
        tags: Maybe[list[str]] = MISSING,
    ) -> ApplicationData:
        data = remove_undefined(
            custom_install_url=custom_install_url,
            description=description,
            role_connections_verification_url=role_connections_verification_url,
            install_params=install_params,
            flags=flags,
            icon=to_datauri(icon) if icon else icon,
            cover_image=to_datauri(cover_image) if cover_image else cover_image,
            interactions_endpoint_url=interactions_endpoint_url,
            tags=tags,
        )

        return cast(
            ApplicationData,
            await self.request(
                'PATCH', Route(self, '/oauth2/applications/@me'), data, t=ApplicationData,
            )
        )

    async def get_gateway_bot(self) -> GetGatewayBotData:
        return cast(
            GetGatewayBotData,
            await self.request(
                'GET', Route(self, '/gateway/bot'), t=GetGatewayBotData,
            )
        )

    # Application Commands
    async def get_global_application_commands(
        self, application_id: int, with_localizations: bool = False
    ) -> list[ApplicationCommandData]:
        return cast(
            list[ApplicationCommandData],
            await self.request(
                'GET',
                Route(
                    self,
                    '/applications/{application_id}/commands', application_id=application_id
                ),
                query_params={'with_localizations': str(with_localizations).lower()},
                t=list[ApplicationCommandData],
            )
        )

    async def create_global_application_command(
        self,
        application_id: int,
        name: str,
        name_localizations: Maybe[dict[str, str]] = MISSING,
        description: Maybe[str] = MISSING,
        description_localizations: Maybe[dict[str, str]] = MISSING,
        options: Maybe[list[ApplicationCommandOptionData]] = MISSING,
        default_member_permissions: Maybe[str | None] = MISSING,
        dm_permission: Maybe[bool | None] = MISSING,
        default_permission: Maybe[bool] = MISSING,
        type: Maybe[ApplicationCommandTypes] = MISSING,
    ) -> ApplicationCommandData:
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return cast(
            ApplicationCommandData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/applications/{application_id}/commands', application_id=application_id
                ),
                data=data,
                t=ApplicationCommandData,
            )
        )

    async def edit_global_application_command(
        self,
        application_id: int,
        command_id: int,
        name: Maybe[str] = MISSING,
        name_localizations: Maybe[dict[str, str]] = MISSING,
        description: Maybe[str] = MISSING,
        description_localizations: Maybe[dict[str, str]] = MISSING,
        options: Maybe[list[ApplicationCommandOptionData]] = MISSING,
        default_member_permissions: Maybe[str | None] = MISSING,
        dm_permission: Maybe[bool | None] = MISSING,
        default_permission: Maybe[bool] = MISSING,
        type: Maybe[ApplicationCommandTypes] = MISSING,
    ) -> ApplicationCommandData:
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return cast(
            ApplicationCommandData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/applications/{application_id}/commands/{command_id}',
                    application_id=application_id,
                    command_id=command_id,
                ),
                data=data,
                t=ApplicationCommandData,
            )
        )

    async def delete_global_application_command(
        self,
        application_id: int,
        command_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/applications/{application_id}/commands/{command_id}',
                    application_id=application_id,
                    command_id=command_id,
                ),
                t=None,
            )
        )

    async def get_guild_application_commands(
        self,
        application_id: int,
        guild_id: int,
        with_localizations: bool = False,
    ) -> list[ApplicationCommandData]:
        return cast(
            list[ApplicationCommandData],
            await self.request(
                'GET',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands',
                    application_id=application_id,
                    guild_id=guild_id,
                ),
                query_params={'with_localizations': str(with_localizations).lower()},
                t=list[ApplicationCommandData],
            )
        )

    async def create_guild_application_command(
        self,
        application_id: int,
        guild_id: int,
        name: str,
        name_localizations: Maybe[dict[str, str]] = MISSING,
        description: Maybe[str] = MISSING,
        description_localizations: Maybe[dict[str, str]] = MISSING,
        options: Maybe[list[ApplicationCommandOptionData]] = MISSING,
        default_member_permissions: Maybe[str | None] = MISSING,
        dm_permission: Maybe[bool | None] = MISSING,
        default_permission: Maybe[bool] = MISSING,
        type: Maybe[ApplicationCommandTypes] = MISSING,
    ) -> ApplicationCommandData:
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return cast(
            ApplicationCommandData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands',
                    application_id=application_id,
                    guild_id=guild_id,
                ),
                data=data,
                t=ApplicationCommandData,
            )
        )

    async def edit_guild_application_command(
        self,
        application_id: int,
        command_id: int,
        guild_id: int,
        name: Maybe[str] = MISSING,
        name_localizations: Maybe[dict[str, str]] = MISSING,
        description: Maybe[str] = MISSING,
        description_localizations: Maybe[dict[str, str]] = MISSING,
        options: Maybe[list[ApplicationCommandOptionData]] = MISSING,
        default_member_permissions: Maybe[str | None] = MISSING,
        dm_permission: Maybe[bool | None] = MISSING,
        default_permission: Maybe[bool] = MISSING,
        type: Maybe[ApplicationCommandTypes] = MISSING,
    ) -> ApplicationCommandData:
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return cast(
            ApplicationCommandData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}',
                    application_id=application_id,
                    guild_id=guild_id,
                    command_id=command_id,
                ),
                data=data,
                t=ApplicationCommandData,
            )
        )

    async def delete_guild_application_command(
        self,
        application_id: int,
        guild_id: int,
        command_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}',
                    application_id=application_id,
                    command_id=command_id,
                    guild_id=guild_id,
                ),
                t=None,
            )
        )

    async def bulk_overwrite_global_commands(
        self, application_id: int, application_commands: list[ApplicationCommandData]
    ) -> list[ApplicationCommandData]:
        return cast(
            list[ApplicationCommandData],
            await self.request(
                'PUT',
                Route(
                    self,
                    '/applications/{application_id}/commands', application_id=application_id
                ),
                application_commands,
                t=list[ApplicationCommandData],
            )
        )

    async def bulk_overwrite_guild_commands(
        self,
        application_id: int,
        guild_id: int,
        application_commands: list[ApplicationCommandData],
    ) -> list[ApplicationCommandData]:
        return cast(
            list[ApplicationCommandData],
            await self.request(
                'PUT',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands',
                    application_id=application_id,
                    guild_id=guild_id,
                ),
                application_commands,
                t=list[ApplicationCommandData],
            )
        )

    async def get_guild_application_command_permissions(
        self, application_id: int, guild_id: int
    ) -> list[GuildApplicationCommandPermissionData]:
        return cast(
            list[GuildApplicationCommandPermissionData],
            await self.request(
                'GET',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands/permissions',
                    guild_id=guild_id,
                    application_id=application_id,
                ),
                t=list[GuildApplicationCommandPermissionData],
            )
        )

    async def get_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int
    ) -> GuildApplicationCommandPermissionData:
        return cast(
            GuildApplicationCommandPermissionData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions',
                    guild_id=guild_id,
                    application_id=application_id,
                    command_id=command_id,
                ),
                t=GuildApplicationCommandPermissionData,
            )
        )

    async def edit_application_command_permissions(
        self,
        application_id: int,
        guild_id: int,
        command_id: int,
        permissions: list[ApplicationCommandPermissionsData],
    ) -> GuildApplicationCommandPermissionData:
        return cast(
            GuildApplicationCommandPermissionData,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions',
                    application_id=application_id,
                    guild_id=guild_id,
                    command_id=command_id,
                ),
                {'permissions': permissions},
                t=GuildApplicationCommandPermissionData,
            )
        )

    # Application Role Connections
    async def get_application_role_connection_metadata_records(
        self,
        application_id: int,
    ) -> list[ApplicationRoleConnectionMetadataData]:
        return cast(
            list[ApplicationRoleConnectionMetadataData],
            await self.request(
                'GET',
                Route(
                    self,
                    '/applications/{application_id}/role-connections/metadata',
                    application_id=application_id,
                ),
                t=list[ApplicationRoleConnectionMetadataData],
            )
        )

    async def update_application_role_connection_metadata_records(
        self,
        application_id: int,
        records: list[ApplicationRoleConnectionMetadataData],
    ) -> list[ApplicationRoleConnectionMetadataData]:
        return cast(
            list[ApplicationRoleConnectionMetadataData],
            await self.request(
                'PUT',
                Route(
                    self,
                    '/applications/{application_id}/role-connections/metadata',
                    application_id=application_id,
                ),
                records,
                t=list[ApplicationRoleConnectionMetadataData],
            )
        )

    # Audit Log
    async def get_guild_audit_log(
        self,
        guild_id: int,
        user_id: Maybe[int] = MISSING,
        action_type: Maybe[AuditLogEvents] = MISSING,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> AuditLogData:
        path = form_qs(
            "/guilds/{guild_id}/audit-logs",
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )

        return cast(
            AuditLogData,
            await self.request(
                "GET",
                Route(self, path, guild_id=guild_id),
                t=AuditLogData,
            ),
        )

    # Auto Moderation
    async def list_auto_moderation_rules_for_guild(
        self, guild_id: int
    ) -> list[AutoModerationRuleData]:
        return cast(
            list[AutoModerationRuleData],
            await self.request(
                'GET',
                Route(
                    self,
                    '/guilds/{guild_id}/auto-moderation/rules',
                    guild_id=guild_id,
                ),
                t=list[AutoModerationRuleData],
            )
        )

    async def get_auto_moderation_rule(
        self,
        guild_id: int,
        rule_id: int,
    ) -> AutoModerationRuleData:
        return cast(
            AutoModerationRuleData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/guilds/{guild_id}/auto-moderation/rules/{rule_id}',
                    guild_id=guild_id,
                    rule_id=rule_id,
                ),
                t=AutoModerationRuleData,
            )
        )

    async def create_auto_moderation_rule(
        self,
        guild_id: int,
        *,
        name: str,
        event_type: AutoModerationEventTypes,
        trigger_type: AutoModerationTriggerTypes,
        actions: list[AutoModerationActionData],
        trigger_metadata: Maybe[AutoModerationTriggerMetadataData] = MISSING,
        enabled: bool = False,
        exempt_roles: Maybe[list[int]] = MISSING,
        exempt_channels: Maybe[list[int]] = MISSING,
        reason: str | None = None,
    ) -> AutoModerationRuleData:
        data = {
            'name': name,
            'event_type': event_type,
            'trigger_type': trigger_type,
            'trigger_metadata': trigger_metadata,
            'actions': actions,
            'enabled': enabled,
            'exampt_roles': exempt_roles,
            'exempt_channels': exempt_channels,
        }
        return cast(
            AutoModerationRuleData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/guilds/{guild_id}/auto-moderation/rules',
                    guild_id=guild_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=AutoModerationRuleData,
            )
        )

    async def modify_auto_moderation_rule(
        self,
        guild_id: int,
        rule_id: int,
        *,
        name: Maybe[str] = MISSING,
        event_type: Maybe[AutoModerationEventTypes] = MISSING,
        actions: Maybe[list[AutoModerationActionData]] = MISSING,
        trigger_metadata: Maybe[AutoModerationTriggerMetadataData | None] = MISSING,
        enabled: Maybe[bool] = MISSING,
        exempt_roles: Maybe[list[int]] = MISSING,
        exempt_channels: Maybe[list[int]] = MISSING,
        reason: str | None = None,
    ) -> AutoModerationRuleData:
        data = {
            'name': name,
            'event_type': event_type,
            'trigger_metadata': trigger_metadata,
            'actions': actions,
            'enabled': enabled,
            'exampt_roles': exempt_roles,
            'exempt_channels': exempt_channels,
        }
        return cast(
            AutoModerationRuleData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/auto-moderation/rules/{rule_id}',
                    guild_id=guild_id,
                    rule_id=rule_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=AutoModerationRuleData,
            )
        )

    async def delete_auto_moderation_rule(
        self, guild_id: int, rule_id: int, *, reason: str | None = None
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/auto-moderation/rules/{rule_id}',
                    guild_id=guild_id,
                    rule_id=rule_id,
                ),
                reason=reason,
                t=None,
            )
        )

    # Channel 
    async def get_channel(
        self,
        channel_id: int,
    ) -> ChannelData:
        return cast(
            ChannelData,
            await self.request(
                'GET', Route(self, '/channels/{channel_id}', channel_id=channel_id), t=ChannelData,
            )
        )

    async def modify_channel(
        self,
        channel_id: int,
        *,
        name: Maybe[str] = MISSING,
        # Group DM Only
        icon: Maybe[File] = MISSING,
        # Thread Only
        archived: Maybe[bool] = MISSING,
        auto_archive_duration: Maybe[int] = MISSING,
        locked: Maybe[bool] = MISSING,
        invitable: Maybe[bool] = MISSING,
        applied_tags: Maybe[list[int]] = MISSING,
        # Thread & Guild Channels
        rate_limit_per_user: Maybe[int | None] = MISSING,
        flags: Maybe[int | None] = MISSING,
        # Guild Channels Only
        type: Maybe[ChannelTypes] = MISSING,
        position: Maybe[int | None] = MISSING,
        topic: Maybe[str | None] = MISSING,
        nsfw: Maybe[bool | None] = MISSING,
        bitrate: Maybe[int | None] = MISSING,
        user_imit: Maybe[int | None] = MISSING,
        permission_overwrites: Maybe[list[PermissionOverwriteData] | None] = MISSING,
        parent_id: Maybe[int | None] = MISSING,
        rtc_region: Maybe[str | None] = MISSING,
        video_quality_mode: Maybe[int | None] = MISSING,
        default_auto_archive_duration: Maybe[int | None] = MISSING,
        available_tags: Maybe[list[ForumTagData] | None] = MISSING,
        default_reaction_emoji: Maybe[DefaultReactionData | None] = MISSING,
        default_thread_rate_limit_per_user: Maybe[int] = MISSING,
        default_sort_order: Maybe[int | None] = MISSING,
        default_forum_layout: Maybe[int] = MISSING,
        # Reason
        reason: str | None = None,
    ) -> ChannelData:
        data = {
            'name': name,
            'icon': to_datauri(icon) if icon else icon,
            'archived': archived,
            'auto_archive_duration': auto_archive_duration,
            'locked': locked,
            'invitable': invitable,
            'applied_tags': applied_tags,
            'rate_limit_per_user': rate_limit_per_user,
            'flags': flags,
            'type': type,
            'position': position,
            'topic': topic,
            'nsfw': nsfw,
            'bitrate': bitrate,
            'user_limit': user_imit,
            'permission_overwrites': permission_overwrites,
            'parent_id': parent_id,
            'rtc_region': rtc_region,
            'video_quality_mode': video_quality_mode,
            'default_auto_archive_duration': default_auto_archive_duration,
            'available_tags': available_tags,
            'default_reaction_emoji': default_reaction_emoji,
            'default_thread_rate_limit_per_user': default_thread_rate_limit_per_user,
            'default_sort_order': default_sort_order,
            'default_forum_layout': default_forum_layout,
        }
        return cast(
            ChannelData,
            await self.request(
                'PATCH',
                Route(self, '/channels/{channel_id}', channel_id=channel_id),
                remove_undefined(**data),
                reason=reason,
                t=ChannelData,
            )
        )

    async def delete_channel(
        self,
        channel_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        cast(
            None,
            await self.request(
                'DELETE',
                Route(self, '/channels/{channel_id}', channel_id=channel_id),
                reason=reason,
                t=None,
            )
        )

    async def get_channel_messages(
        self,
        channel_id: int,
        *,
        around: Maybe[int] = MISSING,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> list[MessageData]:
        path = form_qs(
            '/channels/{channel_id}/messages',
            around=around,
            before=before,
            after=after,
            limit=limit,
        )
        return cast(
            list[MessageData],
            await self.request(
                'GET',
                Route(self, path, channel_id=channel_id),
                t=list[MessageData],
            )
        )

    async def get_channel_message(
        self,
        channel_id: int,
        message_id: int,
    ) -> MessageData:
        return cast(
            MessageData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                t=MessageData,
            )
        )

    async def create_message(
        self,
        channel_id: int,
        *,
        content: Maybe[str] = MISSING,
        nonce: Maybe[str] = MISSING,
        tts: Maybe[bool] = MISSING,
        embeds: Maybe[list[EmbedData]] = MISSING,
        allowed_mentions: Maybe[AllowedMentionsData] = MISSING,
        message_reference: Maybe[MessageReferenceData] = MISSING,
        components: Maybe[list[ComponentData]] = MISSING,
        sticker_ids: Maybe[list[int]] = MISSING,
        files: Maybe[list[File]] = MISSING,
        attachments: Maybe[list[PartialAttachmentData]] = MISSING,
        flags: Maybe[int] = MISSING,
    ) -> MessageData:
        data = remove_undefined(
            content=content,
            nonce=nonce,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=components,
            sticker_ids=sticker_ids,
            attachments=attachments,
            flags=flags,
        )
        return cast(
            MessageData,
            await self.request(
                'POST',
                Route(self, '/channels/{channel_id}/messages', channel_id=channel_id),
                data,
                files=files,
                t=MessageData,
            )
        )

    async def crosspost_message(
        self,
        channel_id: int,
        message_id: int,
    ) -> MessageData:
        return cast(
            MessageData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/crosspost',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                t=MessageData,
            )
        )

    async def create_reaction(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
    ) -> None:
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                    channel_id=channel_id,
                    message_id=message_id,
                    emoji=emoji,
                ),
                t=None,
            )
        )

    async def delete_own_reaction(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                    channel_id=channel_id,
                    message_id=message_id,
                    emoji=emoji,
                ),
                t=None,
            )
        )

    async def delete_user_reaction(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        user_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                    emoji=emoji,
                    user_id=user_id,
                ),
                t=None,
            )
        )

    async def get_reactions(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        *,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = 25,
    ) -> list[UserData]:
        path = form_qs(
            '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
            after=after,
            limit=limit,
        )
        return cast(
            list[UserData],
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                    message_id=message_id,
                    emoji=emoji,
                ),
                t=list[UserData],
            )
        )

    async def delete_all_reactions(
        self,
        channel_id: int,
        message_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/reactions',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                t=None,
            )
        )

    async def delete_all_reactions_for_emoji(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                    channel_id=channel_id,
                    message_id=message_id,
                    emoji=emoji,
                ),
                t=None,
            )
        )

    async def edit_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        content: Maybe[str] = MISSING,
        embeds: Maybe[list[EmbedData]] = MISSING,
        flags: Maybe[int] = MISSING,
        allowed_mentions: Maybe[AllowedMentionsData] = MISSING,
        components: Maybe[list[ComponentData]] = MISSING,
        files: Maybe[list[File]] = MISSING,
        attachments: Maybe[list[PartialAttachmentData]] = MISSING,
    ) -> MessageData:
        data = {
            'content': content,
            'embeds': embeds,
            'flags': flags,
            'allowed_mentions': allowed_mentions,
            'components': components,
            'attachments': attachments,
        }
        return cast(
            MessageData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                remove_undefined(**data),
                files=files,
                t=MessageData,
            )
        )

    async def delete_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def bulk_delete_messages(
        self,
        channel_id: int,
        *,
        messages: list[int],
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'POST',
                Route(self, '/channels/{channel_id}/messages/bulk-delete', channel_id=channel_id),
                {'messages': messages},
                reason=reason,
                t=None,
            )
        )

    async def edit_channel_permissions(
        self,
        channel_id: int,
        overwrite_id: int,
        *,
        type: int,
        allow: Maybe[int | None] = MISSING,
        deny: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> None:
        data = {
            'allow': str(allow),
            'deny': str(deny),
            'type': type,
        }
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/permissions/{overwrite_id}',
                    channel_id=channel_id,
                    overwrite_id=overwrite_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=None,
            )
        )

    async def get_channel_invites(
        self,
        channel_id: int,
    ) -> list[InviteData]:
        return cast(
            list[InviteData],
            await self.request(
                'GET', Route(self, '/channels/{channel_id}/invites', channel_id=channel_id), t=list[InviteData],
            )
        )

    async def create_channel_invite(
        self,
        channel_id: int,
        *,
        max_age: Maybe[int] = MISSING,
        max_uses: Maybe[int] = MISSING,
        temporary: Maybe[bool] = MISSING,
        unique: Maybe[bool] = MISSING,
        target_type: Maybe[int] = MISSING,
        target_user_id: Maybe[int] = MISSING,
        target_application_id: Maybe[int] = MISSING,
        reason: str | None = None,
    ) -> InviteData:
        data = {
            'max_age': max_age,
            'max_uses': max_uses,
            'temporary': temporary,
            'unique': unique,
            'target_type': target_type,
            'target_user_id': target_user_id,
            'target_application_id': target_application_id,
        }
        return cast(
            InviteData,
            await self.request(
                'POST',
                Route(self, '/channels/{channel_id}/invites', channel_id=channel_id),
                remove_undefined(**data),
                reason=reason,
                t=InviteData
            )
        )

    async def delete_channel_permission(
        self,
        channel_id: int,
        overwrite_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/permissions/{overwrite_id}',
                    channel_id=channel_id,
                    overwrite_id=overwrite_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def follow_announcement_channel(
        self,
        channel_id: int,
        *,
        webhook_channel_id: int,
    ) -> FollowedChannelData:
        data = {
            'webhook_channel_id': webhook_channel_id,
        }
        return cast(
            FollowedChannelData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/channels/{channel_id}/followers',
                    channel_id=channel_id,
                ),
                data,
                t=FollowedChannelData,
            )
        )

    async def trigger_typing_indicator(
        self,
        channel_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'POST', Route(self, '/channels/{channel_id}/typing', channel_id=channel_id), t=None
            )
        )

    async def get_pinned_messages(
        self,
        channel_id: int,
    ) -> list[MessageData]:
        return cast(
            list[MessageData],
            await self.request(
                'GET', Route(self, '/channels/{channel_id}/pins', channel_id=channel_id), t=list[MessageData],
            )
        )

    async def pin_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/pins/{message_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def unpin_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/pins/{message_id}',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def group_dm_add_recipient(
        self,
        channel_id: int,
        user_id: int,
        *,
        access_token: str,
        nick: Maybe[str | None] = MISSING,
    ) -> None:
        data = {
            'access_token': access_token,
            'nick': nick,
        }
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/recipients/{user_id}',
                    channel_id=channel_id,
                    user_id=user_id,
                ),
                data,
                t=None,
            )
        )

    async def group_dm_remove_recipient(
        self,
        channel_id: int,
        user_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/recipients/{user_id}',
                    channel_id=channel_id,
                    user_id=user_id,
                ),
                t=None,
            )
        )

    async def start_thread_from_message(
        self,
        channel_id: int,
        message_id: int,
        *,
        name: str,
        auto_archive_duration: Maybe[int] = MISSING,
        rate_limit_per_user: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> ChannelData:
        data = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
        }
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/channels/{channel_id}/messages/{message_id}/threads',
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=ChannelData,
            )
        )

    async def start_thread_without_message(
        self,
        channel_id: int,
        *,
        name: str,
        auto_archive_duration: Maybe[int] = MISSING,
        type: Maybe[ChannelTypes] = MISSING,
        invitable: Maybe[bool] = MISSING,
        rate_limit_per_user: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> ChannelData:
        data = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'type': type,
            'invitable': invitable,
            'rate_limit_per_user': rate_limit_per_user,
        }
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/channels/{channel_id}/threads',
                    channel_id=channel_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=ChannelData,
            )
        )

    async def start_thread_in_forum_channel(
        self,
        channel_id: int,
        *,
        name: str,
        auto_archive_duration: Maybe[int] = MISSING,
        rate_limit_per_user: Maybe[int | None] = MISSING,
        message: ForumThreadMessageParams,
        applied_tags: Maybe[list[int]] = MISSING,
        files: Maybe[list[File]] = MISSING,
        reason: str | None = None,
    ) -> ChannelData:
        data = remove_undefined(
            **{
                'name': name,
                'auto_archive_duration': auto_archive_duration,
                'rate_limit_per_user': rate_limit_per_user,
                'message': message,
                'applied_tags': applied_tags,
            }
        )
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(
                    self,
                    '/channels/{channel_id}/threads',
                    channel_id=channel_id,
                ),
                data=data,
                files=files,
                reason=reason,
                t=ChannelData,
            )
        )

    async def join_thread(
        self,
        channel_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/thread-members/@me',
                    channel_id=channel_id,
                ),
                t=None,
            )
        )

    async def add_thread_member(
        self,
        channel_id: int,
        user_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/channels/{channel_id}/thread-members/{user_id}',
                    channel_id=channel_id,
                    user_id=user_id,
                ),
                t=None,
            )
        )

    async def leave_thread(
        self,
        channel_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/thread-members/@me',
                    channel_id=channel_id,
                ),
                t=None,
            )
        )

    async def remove_thread_member(
        self,
        channel_id: int,
        user_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/channels/{channel_id}/thread-members/{user_id}',
                    channel_id=channel_id,
                    user_id=user_id,
                ),
                t=None,
            )
        )

    async def get_thread_member(
        self,
        channel_id: int,
        user_id: int,
        *,
        with_member: Maybe[bool] = MISSING,
    ) -> ThreadMemberData:
        path = form_qs(
            '/channels/{channel_id}/thread-members/{user_id}',
            with_member=with_member,
        )
        return cast(
            ThreadMemberData,
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                    user_id=user_id,
                ),
                t=ThreadMemberData,
            )
        )

    async def list_thread_members(
        self,
        channel_id: int,
        *,
        with_member: Maybe[bool] = MISSING,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> list[ThreadMemberData]:
        path = form_qs(
            '/channels/{channel_id}/thread-members',
            with_member=with_member,
            after=after,
            limit=limit,
        )
        return cast(
            list[ThreadMemberData],
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                ),
                t=list[ThreadMemberData],
            )
        )

    async def list_public_archived_threads(
        self,
        channel_id: int,
        *,
        before: Maybe[str] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> HasMoreListThreadsData:
        path = form_qs(
            '/channels/{channel_id}/threads/archived/public',
            before=before,
            limit=limit,
        )
        return cast(
            HasMoreListThreadsData,
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                ),
                t=HasMoreListThreadsData,
            )
        )

    async def list_private_archived_threads(
        self,
        channel_id: int,
        *,
        before: Maybe[str] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> HasMoreListThreadsData:
        path = form_qs(
            '/channels/{channel_id}/threads/archived/private',
            before=before,
            limit=limit,
        )
        return cast(
            HasMoreListThreadsData,
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                ),
                t=HasMoreListThreadsData,
            )
        )

    async def list_joined_private_archived_threads(
        self,
        channel_id: int,
        *,
        before: Maybe[str] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> HasMoreListThreadsData:
        path = form_qs(
            '/channels/{channel_id}/users/@me/threads/archived/private',
            before=before,
            limit=limit,
        )
        return cast(
            HasMoreListThreadsData,
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    channel_id=channel_id,
                ),
                t=HasMoreListThreadsData,
            )
        )

    # Emojis
    async def list_guild_emojis(self, guild_id: int) -> list[EmojiData]:
        return cast(
            list[EmojiData],
            await self.request(
                'GET', Route(self, '/guilds/{guild_id}/emojis', guild_id=guild_id), t=list[EmojiData],
            )
        )

    async def get_guild_emoji(self, guild_id: int, emoji_id: int) -> EmojiData:
        return cast(
            EmojiData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/guilds/{guild_id}/emojis/{emoji_id}',
                    guild_id=guild_id,
                    emoji_id=emoji_id,
                ),
                t=EmojiData
            )
        )

    async def create_guild_emoji(
        self,
        guild_id: int,
        *,
        name: str,
        image: File,
        roles: list[int] | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> EmojiData:
        payload = {
            'name': name,
            'image': to_datauri(image),
            'roles': roles,
        }
        return cast(
            EmojiData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/emojis', guild_id=guild_id),
                remove_undefined(**payload),
                reason=reason,
                t=EmojiData
            )
        )

    async def modify_guild_emoji(
        self,
        guild_id: int,
        emoji_id: int,
        *,
        name: str | MissingEnum = MISSING,
        roles: list[int] | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> EmojiData:
        payload = {
            'name': name,
            'roles': roles,
        }
        return cast(
            EmojiData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/emojis/{emoji_id}',
                    guild_id=guild_id,
                    emoji_id=emoji_id,
                ),
                remove_undefined(**payload),
                reason=reason,
                t=EmojiData,
            )
        )

    async def delete_guild_emoji(
        self,
        guild_id: int,
        emoji_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/emojis/{emoji_id}',
                    guild_id=guild_id,
                    emoji_id=emoji_id,
                ),
                reason=reason,
                t=None,
            )
        )

    # Guild
    async def get_guild(self, guild_id: int, with_counts: bool = False) -> GuildData:
        path = form_qs(
            '/guilds/{guild_id}',
            with_counts=with_counts,
        )
        return cast(
            GuildData,
            await self.request(
                'GET', Route(self, path, guild_id=guild_id), t=GuildData,
            )
        )

    async def get_guild_preview(self, guild_id: int) -> GuildPreviewData:
        return cast(
            GuildPreviewData,
            await self.request(
                'GET', Route(self, '/guilds/{guild_id}/preview', guild_id=guild_id), t=GuildPreviewData,
            )
        )

    async def modify_guild(
        self,
        guild_id: int,
        *,
        name: Maybe[str] = MISSING,
        verification_level: Maybe[VerificationLevels | None] = MISSING,
        default_message_notifications: Maybe[DefaultMessageNotificationLevels | None] = MISSING,
        explicit_content_filter: Maybe[ExplicitContentFilterLevels | None] = MISSING,
        afk_channel_id: Maybe[int | None] = MISSING,
        afk_timeout: Maybe[int] = MISSING,
        icon: Maybe[File | None] = MISSING,
        owner_id: Maybe[int] = MISSING,
        splash: Maybe[File | None] = MISSING,
        discovery_splash: Maybe[File | None] = MISSING,
        banner: Maybe[File | None] = MISSING,
        system_channel_id: Maybe[int | None] = MISSING,
        system_channel_flags: Maybe[int] = MISSING,
        rules_channel_id: Maybe[int | None] = MISSING,
        public_updates_channel_id: Maybe[int | None] = MISSING,
        preferred_locale: Maybe[str | None] = MISSING,
        features: Maybe[list[GuildFeatures]] = MISSING,
        description: Maybe[str | None] = MISSING,
        premium_progress_bar_enabled: Maybe[bool] = MISSING,
        safety_alerts_channel_id: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> GuildData:
        data = {
            'name': name,
            'verification_level': verification_level,
            'default_message_notifications': default_message_notifications,
            'explicit_content_filter': explicit_content_filter,
            'afk_channel_id': afk_channel_id,
            'afk_timeout': afk_timeout,
            'icon': to_datauri(icon) if icon else icon,
            'owner_id': owner_id,
            'splash': to_datauri(splash) if splash else splash,
            'discovery_splash': to_datauri(discovery_splash) if discovery_splash else discovery_splash,
            'banner': to_datauri(banner) if banner else banner,
            'system_channel_id': system_channel_id,
            'system_channel_flags': system_channel_flags,
            'rules_channel_id': rules_channel_id,
            'public_updates_channel_id': public_updates_channel_id,
            'preferred_locale': preferred_locale,
            'features': features,
            'description': description,
            'premium_progress_bar_enabled': premium_progress_bar_enabled,
            'safety_alerts_channel_id': safety_alerts_channel_id,
        }
        return cast(
            GuildData,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}', guild_id=guild_id),
                remove_undefined(**data),
                reason=reason,
                t=GuildData,
            )
        )

    async def delete_guild(self, guild_id: int) -> None:
        return cast(
            None,
            await self.request(
                'DELETE', Route(self, '/guilds/{guild_id}', guild_id=guild_id), t=None,
            )
        )

    async def get_guild_channels(self, guild_id: int) -> list[ChannelData]:
        return cast(
            list[ChannelData],
            await self.request(
                'GET', Route(self, '/guilds/{guild_id}/channels', guild_id=guild_id), t=list[ChannelData],
            )
        )

    async def create_guild_channel(
        self,
        guild_id: int,
        *,
        name: str,
        type: Maybe[ChannelTypes | None],
        topic: Maybe[str | None] = MISSING,
        bitrate: Maybe[int | None] = MISSING,
        user_limit: Maybe[int | None] = MISSING,
        rate_limit_per_user: Maybe[int | None] = MISSING,
        position: Maybe[int | None] = MISSING,
        permission_overwrites: Maybe[list[PermissionOverwriteData] | None] = MISSING,
        parent_id: Maybe[int | None] = MISSING,
        nsfw: Maybe[bool | None] = MISSING,
        rtc_region: Maybe[str | None] = MISSING,
        video_quality_mode: Maybe[int | None] = MISSING,
        default_auto_archive_duration: Maybe[int | None] = MISSING,
        default_reaction_emoji: Maybe[DefaultReactionData | None] = MISSING,
        available_tags: Maybe[list[ForumTagData] | None] = MISSING,
        default_sort_order: Maybe[SortOrderTypes | None] = MISSING,
        default_forum_layout: Maybe[ForumLayoutTypes | None] = MISSING,
        default_thread_rate_limit_per_user: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> ChannelData:
        data = remove_undefined(
            name=name,
            type=type,
            topic=topic,
            bitrate=bitrate,
            user_limit=user_limit,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            permission_overwrites=permission_overwrites,
            parent_id=parent_id,
            nsfw=nsfw,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            default_auto_archive_duration=default_auto_archive_duration,
            default_reaction_emoji=default_reaction_emoji,
            available_tags=available_tags,
            default_sort_order=default_sort_order,
            default_forum_layout=default_forum_layout,
            default_thread_rate_limit_per_user=default_thread_rate_limit_per_user,
        )
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/channels', guild_id=guild_id),
                data,
                reason=reason,
                t=ChannelData,
            )
        )

    async def modify_guild_channel_positions(
        self,
        guild_id: int,
        channels: list[ChannelPositionUpdateData],
    ) -> None:
        return cast(
            None,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/channels', guild_id=guild_id),
                channels,
                t=None,
            )
        )

    async def list_active_guild_threads(
        self,
        guild_id: int,
    ) -> list[ChannelData]:
        return cast(
            list[ChannelData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/threads/active', guild_id=guild_id),
                t=list[ChannelData],
            )
        )

    async def get_guild_member(self, guild_id: int, user_id: int) -> GuildMemberData:
        return cast(
            GuildMemberData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                t=GuildMemberData,
            )
        )

    async def list_guild_members(
        self,
        guild_id: int,
        *,
        limit: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
    ) -> list[GuildMemberData]:
        path = form_qs(
            '/guilds/{guild_id}/members',
            limit=limit,
            after=after,
        )
        return cast(
            list[GuildMemberData],
            await self.request(
                'GET',
                Route(self, path, guild_id=guild_id),
                t=list[GuildMemberData],
            )
        )

    async def search_guild_members(
        self,
        guild_id: int,
        query: str,
        *,
        limit: Maybe[int] = MISSING,
    ) -> list[GuildMemberData]:
        path = form_qs(
            '/guilds/{guild_id}/members/search',
            query=query,
            limit=limit,
        )
        return cast(
            list[GuildMemberData],
            await self.request(
                'GET',
                Route(self, path, guild_id=guild_id),
                t=list[GuildMemberData],
            )
        )

    async def add_guild_member(
        self,
        guild_id: int,
        user_id: int,
        *,
        access_token: str,
        nick: Maybe[str | None] = MISSING,
        roles: Maybe[list[int]] = MISSING,
        mute: Maybe[bool] = MISSING,
        deaf: Maybe[bool] = MISSING,
        reason: str | None = None,
    ) -> GuildMemberData:
        data = {
            'access_token': access_token,
            'nick': nick,
            'roles': roles,
            'mute': mute,
            'deaf': deaf,
        }
        return cast(
            GuildMemberData,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=GuildMemberData,
            )
        )

    async def modify_guild_member(
        self,
        guild_id: int,
        user_id: int,
        *,
        nick: Maybe[str | None] = MISSING,
        roles: Maybe[list[int]] = MISSING,
        mute: Maybe[bool | None] = MISSING,
        deaf: Maybe[bool | None] = MISSING,
        channel_id: Maybe[int | None] = MISSING,
        communication_disabled_until: Maybe[datetime | None] = MISSING,
        flags: Maybe[int | None] = MISSING,
        reason: str | None = None,
    ) -> GuildMemberData:
        data = {
            'nick': nick,
            'roles': roles,
            'mute': mute,
            'deaf': deaf,
            'channel_id': channel_id,
            'communication_disabled_until': communication_disabled_until.isoformat() if communication_disabled_until else communication_disabled_until,
            'flags': flags,
        }
        return cast(
            GuildMemberData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=GuildMemberData,
            )
        )

    async def modify_current_member(
        self,
        guild_id: int,
        *,
        nick: Maybe[str | None] = MISSING,
        reason: str | None = None,
    ) -> GuildMemberData:
        data = {
            'nick': nick,
        }
        return cast(
            GuildMemberData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/members/@me',
                    guild_id=guild_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=GuildMemberData,
            )
        )

    async def add_guild_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                    role_id=role_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def remove_guild_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                    role_id=role_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def remove_guild_member(
        self,
        guild_id: int,
        user_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/members/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def get_guild_bans(
        self,
        guild_id: int,
        limit: Maybe[int] = MISSING,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
    ) -> list[BanData]:
        path = form_qs(
            '/guilds/{guild_id}/bans',
            limit=limit,
            before=before,
            after=after,
        )
        return cast(
            list[BanData],
            await self.request(
                'GET', Route(self, path, guild_id=guild_id), t=list[BanData],
            )
        )

    async def get_guild_ban(
        self,
        guild_id: int,
        user_id: int,
    ) -> BanData:
        return cast(
            BanData,
            await self.request(
                'GET',
                Route(
                    self,
                    '/guilds/{guild_id}/bans/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                t=BanData,
            )
        )

    async def create_guild_ban(
        self,
        guild_id: int,
        user_id: int,
        *,
        delete_message_seconds: Maybe[int] = MISSING,
        reason: str | None = None,
    ) -> None:
        data = {
            'delete_message_seconds': delete_message_seconds,
        }
        return cast(
            None,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/guilds/{guild_id}/bans/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=None,
            )
        )

    async def remove_guild_ban(
        self,
        guild_id: int,
        user_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/bans/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def get_guild_roles(
        self,
        guild_id: int,
    ) -> list[RoleData]:
        return cast(
            list[RoleData],
            await self.request(
                'GET', Route(self, '/guilds/{guild_id}/roles', guild_id=guild_id), t=list[RoleData],
            )
        )

    async def create_guild_role(
        self,
        guild_id: int,
        *,
        name: Maybe[str] = MISSING,
        permissions: Maybe[str] = MISSING,
        color: Maybe[int] = MISSING,
        hoist: Maybe[bool] = MISSING,
        icon: Maybe[File | None] = MISSING,
        unicode_emoji: Maybe[str | None] = MISSING,
        mentionable: Maybe[bool] = MISSING,
        reason: str | None = None,
    ) -> RoleData:
        data = {
            'name': name,
            'permissions': permissions,
            'color': color,
            'hoist': hoist,
            'icon': to_datauri(icon) if icon else icon,
            'unicode_emoji': unicode_emoji,
            'mentionable': mentionable,
        }
        return cast(
            RoleData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/roles', guild_id=guild_id),
                remove_undefined(**data),
                reason=reason,
                t=RoleData,
            )
        )

    async def modify_guild_role_positions(
        self,
        guild_id: int,
        roles: list[RolePositionUpdateData],
    ) -> list[RoleData]:
        return cast(
            list[RoleData],
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/roles', guild_id=guild_id),
                roles,
                t=list[RoleData],
            )
        )

    async def modify_guild_role(
        self,
        guild_id: int,
        role_id: int,
        *,
        name: Maybe[str] = MISSING,
        permissions: Maybe[str] = MISSING,
        color: Maybe[int] = MISSING,
        hoist: Maybe[bool] = MISSING,
        icon: Maybe[File | None] = MISSING,
        unicode_emoji: Maybe[str | None] = MISSING,
        mentionable: Maybe[bool] = MISSING,
        reason: str | None = None,
    ) -> RoleData:
        data = {
            'name': name,
            'permissions': permissions,
            'color': color,
            'hoist': hoist,
            'icon': to_datauri(icon) if icon else icon,
            'unicode_emoji': unicode_emoji,
            'mentionable': mentionable,
        }
        return cast(
            RoleData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/roles/{role_id}',
                    guild_id=guild_id,
                    role_id=role_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=RoleData,
            )
        )

    async def modify_guild_mfa_level(
        self,
        guild_id: int,
        *,
        level: MFALevels,
        reason: str | None = None,
    ) -> MFALevelResponse:
        data = {
            'mfa_level': level,
        }
        return cast(
            MFALevelResponse,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}', guild_id=guild_id),
                data,
                reason=reason,
                t=MFALevelResponse,
            )
        )

    async def delete_guild_role(
        self,
        guild_id: int,
        role_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/roles/{role_id}',
                    guild_id=guild_id,
                    role_id=role_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def get_guild_prune_count(
        self,
        guild_id: int,
        *,
        days: Maybe[int] = MISSING,
        include_roles: Maybe[list[int]] = MISSING,
    ) -> PruneCountResponse:
        path = form_qs(
            '/guilds/{guild_id}/prune',
            days=days,
            include_roles=include_roles,
        )
        return cast(
            PruneCountResponse,
            await self.request(
                'GET',
                Route(self, path, guild_id=guild_id),
                t=PruneCountResponse,
            )
        )

    async def begin_guild_prune(
        self,
        guild_id: int,
        *,
        days: Maybe[int] = MISSING,
        compute_prune_count: Maybe[bool] = MISSING,
        include_roles: Maybe[list[int]] = MISSING,
        reason: str | None = None,
    ) -> PruneCountResponse:
        data = {
            'days': days,
            'compute_prune_count': compute_prune_count,
            'include_roles': include_roles,
        }
        return cast(
            PruneCountResponse,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/prune', guild_id=guild_id),
                remove_undefined(**data),
                reason=reason,
                t=PruneCountResponse,
            )
        )

    async def get_guild_voice_regions(
        self,
        guild_id: int,
    ) -> list[VoiceRegionData]:
        return cast(
            list[VoiceRegionData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/regions', guild_id=guild_id),
                t=list[VoiceRegionData],
            )
        )

    async def get_guild_invites(
        self,
        guild_id: int,
    ) -> list[InviteData]:
        return cast(
            list[InviteData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/invites', guild_id=guild_id),
                t=list[InviteData],
            )
        )

    async def get_guild_integrations(
        self,
        guild_id: int,
    ) -> list[IntegrationData]:
        return cast(
            list[IntegrationData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/integrations', guild_id=guild_id),
                t=list[IntegrationData],
            )
        )

    async def delete_guild_integration(
        self,
        guild_id: int,
        integration_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/integrations/{integration_id}',
                    guild_id=guild_id,
                    integration_id=integration_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def get_guild_widget_settings(
        self,
        guild_id: int,
    ) -> GuildWidgetSettingsData:
        return cast(
            GuildWidgetSettingsData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/widget', guild_id=guild_id),
                t=GuildWidgetSettingsData,
            )
        )

    async def modify_guild_widget(
        self,
        guild_id: int,
        *,
        enabled: bool,
        channel_id: int | None,
        reason: str | None = None,
    ) -> GuildWidgetSettingsData:
        data = {
            'enabled': enabled,
            'channel_id': channel_id,
        }
        return cast(
            GuildWidgetSettingsData,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/widget', guild_id=guild_id),
                data,
                reason=reason,
                t=GuildWidgetSettingsData,
            )
        )

    async def get_guild_widget(
        self,
        guild_id: int,
    ) -> GuildWidgetData:
        return cast(
            GuildWidgetData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/widget.json', guild_id=guild_id),
                t=GuildWidgetData,
            )
        )

    async def get_guild_vanity_url(
        self,
        guild_id: int,
    ) -> VanityURLData:
        return cast(
            VanityURLData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/vanity-url', guild_id=guild_id),
                t=VanityURLData,
            )
        )

    async def get_guild_widget_image(
        self,
        guild_id: int,
        *,
        style: Maybe[Literal["shield", "banner1", "banner2", "banner3", "banner4"]] = MISSING,
    ) -> bytes:
        path = form_qs(
            '/guilds/{guild_id}/widget.png',
            style=style,
        )
        return cast(
            bytes,
            await self.request(
                'GET',
                Route(self, path, guild_id=guild_id),
                t=bytes,
            )
        )

    async def get_guild_welcome_screen(
        self,
        guild_id: int,
    ) -> WelcomeScreenData:
        return cast(
            WelcomeScreenData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/welcome-screen', guild_id=guild_id),
                t=WelcomeScreenData,
            )
        )

    async def modify_guild_welcome_screen(
        self,
        guild_id: int,
        *,
        enabled: Maybe[bool | None] = MISSING,
        welcome_channels: Maybe[list[WelcomeChannelData] | None] = MISSING,
        description: Maybe[str | None] = MISSING,
        reason: str | None = None,
    ) -> WelcomeScreenData:
        data = {
            'enabled': enabled,
            'welcome_channels': welcome_channels,
            'description': description,
        }
        return cast(
            WelcomeScreenData,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/welcome-screen', guild_id=guild_id),
                remove_undefined(**data),
                reason=reason,
                t=WelcomeScreenData,
            )
        )

    async def get_guild_onboarding(
        self,
        guild_id: int,
    ) -> GuildOnboardingData:
        return cast(
            GuildOnboardingData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/onboarding', guild_id=guild_id),
                t=GuildOnboardingData,
            )
        )

    async def modify_guild_onboarding(
        self,
        guild_id: int,
        *,
        prompts: list[GuildOnboardingPromptsData],
        default_channel_ids: list[int],
        enabled: bool,
        mode: GuildOnboardingModes,
        reason: str | None = None,
    ) -> GuildOnboardingData:
        data = {
            'prompts': prompts,
            'default_channel_ids': default_channel_ids,
            'enabled': enabled,
            'mode': mode,
        }
        return cast(
            GuildOnboardingData,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/onboarding', guild_id=guild_id),
                remove_undefined(**data),
                reason=reason,
                t=GuildOnboardingData,
            )
        )

    async def modify_current_user_voice_state(
        self,
        guild_id: int,
        *,
        channel_id: Maybe[int] = MISSING,
        suppress: Maybe[bool] = MISSING,
        request_to_speak_timestamp: Maybe[datetime | None] = MISSING,
    ) -> None:
        data = {
            'channel_id': channel_id,
            'suppress': suppress,
            'request_to_speak_timestamp': request_to_speak_timestamp.isoformat() if request_to_speak_timestamp else request_to_speak_timestamp,
        }
        return cast(
            None,
            await self.request(
                'PATCH',
                Route(self, '/guilds/{guild_id}/voice-states/@me', guild_id=guild_id),
                remove_undefined(**data),
                t=None,
            )
        )

    async def modify_user_voice_state(
        self,
        guild_id: int,
        user_id: int,
        *,
        channel_id: Maybe[int] = MISSING,
        suppress: Maybe[bool] = MISSING,
    ) -> None:
        data = {
            'channel_id': channel_id,
            'suppress': suppress,
        }
        return cast(
            None,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/voice-states/{user_id}',
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                remove_undefined(**data),
                t=None,
            )
        )

    # Guild Scheduled Event
    async def list_scheduled_events_for_guild(
        self,
        guild_id: int,
        *,
        with_user_count: Maybe[bool] = MISSING,
    ) -> list[GuildScheduledEventData]:
        path = form_qs(
            '/guilds/{guild_id}/scheduled-events',
            with_user_count=with_user_count,
        )
        return cast(
            list[GuildScheduledEventData],
            await self.request(
                'GET',
                Route(self, path, guild_id=guild_id),
                t=list[GuildScheduledEventData],
            )
        )

    async def create_guild_scheduled_event(
        self,
        guild_id: int,
        *,
        channel_id: int,
        entity_metadata: Maybe[GuildScheduledEventEntityMetadataData] = MISSING,
        name: str,
        privacy_level: GuildScheduledEventPrivacyLevels,
        scheduled_start_time: datetime,
        scheduled_end_time: Maybe[datetime] = MISSING,
        description: Maybe[str] = MISSING,
        entity_type: GuildScheduledEventEntityTypes,
        image: Maybe[File | None] = MISSING,
        reason: str | None = None,
    ) -> GuildScheduledEventData:
        data = {
            'channel_id': channel_id,
            'entity_metadata': entity_metadata,
            'name': name,
            'privacy_level': privacy_level,
            'scheduled_start_time': scheduled_start_time.isoformat(),
            'scheduled_end_time': scheduled_end_time.isoformat() if scheduled_end_time else scheduled_end_time,
            'description': description,
            'entity_type': entity_type,
            'image': to_datauri(image) if image else image,
        }
        return cast(
            GuildScheduledEventData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/scheduled-events', guild_id=guild_id),
                data,
                reason=reason,
                t=GuildScheduledEventData,
            )
        )

    async def get_guild_scheduled_event(
        self,
        guild_id: int,
        event_id: int,
        *,
        with_user_count: Maybe[bool] = MISSING,
    ) -> GuildScheduledEventData:
        path = form_qs(
            '/guilds/{guild_id}/scheduled-events/{event_id}',
            with_user_count=with_user_count,
        )
        return cast(
            GuildScheduledEventData,
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    guild_id=guild_id,
                    event_id=event_id,
                ),
                t=GuildScheduledEventData,
            )
        )

    async def modify_guild_scheduled_event(
        self,
        guild_id: int,
        event_id: int,
        *,
        channel_id: Maybe[int] = MISSING,
        entity_metadata: Maybe[GuildScheduledEventEntityMetadataData | None] = MISSING,
        name: Maybe[str] = MISSING,
        privacy_level: Maybe[GuildScheduledEventPrivacyLevels] = MISSING,
        scheduled_start_time: Maybe[datetime] = MISSING,
        scheduled_end_time: Maybe[datetime] = MISSING,
        description: Maybe[str | None] = MISSING,
        entity_type: Maybe[GuildScheduledEventEntityTypes] = MISSING,
        status: Maybe[GuildScheduledEventStatus] = MISSING,
        image: Maybe[File | None] = MISSING,
        reason: str | None = None,
    ) -> GuildScheduledEventData:
        data = {
            'channel_id': channel_id,
            'entity_metadata': entity_metadata,
            'name': name,
            'privacy_level': privacy_level,
            'scheduled_start_time': scheduled_start_time.isoformat() if scheduled_start_time else scheduled_start_time,
            'scheduled_end_time': scheduled_end_time.isoformat() if scheduled_end_time else scheduled_end_time,
            'description': description,
            'entity_type': entity_type,
            'status': status,
            'image': to_datauri(image) if image else image,
        }
        return cast(
            GuildScheduledEventData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/scheduled-events/{event_id}',
                    guild_id=guild_id,
                    event_id=event_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=GuildScheduledEventData,
            )
        )

    async def delete_guild_scheduled_event(
        self,
        guild_id: int,
        event_id: int,
        *,
        reason: str | None = None,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/scheduled-events/{event_id}',
                    guild_id=guild_id,
                    event_id=event_id,
                ),
                reason=reason,
                t=None,
            )
        )

    async def get_guild_scheduled_event_users(
        self,
        guild_id: int,
        event_id: int,
        *,
        limit: Maybe[int] = MISSING,
        with_member: Maybe[bool] = MISSING,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
    ) -> list[GuildScheduledEventUserData]:
        path = form_qs(
            '/guilds/{guild_id}/scheduled-events/{event_id}/users',
            limit=limit,
            with_member=with_member,
            before=before,
            after=after,
        )
        return cast(
            list[GuildScheduledEventUserData],
            await self.request(
                'GET',
                Route(
                    self,
                    path,
                    guild_id=guild_id,
                    event_id=event_id,
                ),
                t=list[GuildScheduledEventUserData],
            )
        )

    # Guild Template
    async def get_guild_template(
        self,
        template_code: str,
    ) -> GuildTemplateData:
        return cast(
            GuildTemplateData,
            await self.request(
                'GET',
                Route(self, '/guilds/templates/{template_code}', template_code=template_code),
                t=GuildTemplateData,
            )
        )

    async def create_guild_from_guild_template(
        self,
        template_code: str,
        *,
        name: str,
        icon: Maybe[File | None] = MISSING,
    ) -> GuildData:
        data = {
            'name': name,
            'icon': to_datauri(icon) if icon else icon,
        }
        return cast(
            GuildData,
            await self.request(
                'POST',
                Route(self, '/guilds/templates/{template_code}', template_code=template_code),
                remove_undefined(**data),
                t=GuildData,
            )
        )

    async def get_guild_templates(
        self,
        guild_id: int,
    ) -> list[GuildTemplateData]:
        return cast(
            list[GuildTemplateData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/templates', guild_id=guild_id),
                t=list[GuildTemplateData],
            )
        )

    async def create_guild_template(
        self,
        guild_id: int,
        *,
        name: str,
        description: Maybe[str | None] = MISSING,
    ) -> GuildTemplateData:
        data = {
            'name': name,
            'description': description,
        }
        return cast(
            GuildTemplateData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/templates', guild_id=guild_id),
                remove_undefined(**data),
                t=GuildTemplateData,
            )
        )

    async def sync_guild_template(
        self,
        guild_id: int,
        template_code: str,
    ) -> GuildTemplateData:
        return cast(
            GuildTemplateData,
            await self.request(
                'PUT',
                Route(
                    self,
                    '/guilds/{guild_id}/templates/{template_code}',
                    guild_id=guild_id,
                    template_code=template_code,
                ),
                t=GuildTemplateData,
            )
        )

    async def modify_guild_template(
        self,
        guild_id: int,
        template_code: str,
        *,
        name: Maybe[str] = MISSING,
        description: Maybe[str | None] = MISSING,
    ) -> GuildTemplateData:
        data = {
            'name': name,
            'description': description,
        }
        return cast(
            GuildTemplateData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/templates/{template_code}',
                    guild_id=guild_id,
                    template_code=template_code,
                ),
                remove_undefined(**data),
                t=GuildTemplateData,
            )
        )

    async def delete_guild_template(
        self,
        guild_id: int,
        template_code: str,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/templates/{template_code}',
                    guild_id=guild_id,
                    template_code=template_code,
                ),
                t=None,
            )
        )

    # Invites
    async def get_invite(
        self,
        invite_code: str,
        *,
        with_counts: Maybe[bool] = MISSING,
        with_expiration: Maybe[bool] = MISSING,
        guild_scheduled_event_id: Maybe[int] = MISSING,
    ) -> InviteData:
        path = form_qs(
            '/invites/{invite_code}',
            with_counts=with_counts,
            with_expiration=with_expiration,
            guild_scheduled_event_id=guild_scheduled_event_id,
        )
        return cast(
            InviteData,
            await self.request(
                'GET',
                Route(self, path, invite_code=invite_code),
                t=InviteData,
            )
        )

    async def delete_invite(
        self,
        invite_code: str,
        *,
        reason: str | None = None,
    ) -> InviteData:
        return cast(
            InviteData,
            await self.request(
                'DELETE',
                Route(self, '/invites/{invite_code}', invite_code=invite_code),
                reason=reason,
                t=InviteData,
            )
        )

    # Stage Instance
    async def create_stage_instance(
        self,
        channel_id: int,
        *,
        topic: str,
        privacy_level: Maybe[StageInstancePrivacyLevels] = MISSING,
        send_start_notification: Maybe[bool] = MISSING,
        guild_scheduled_event_id: Maybe[int] = MISSING,
        reason: str | None = None,
    ) -> StageInstanceData:
        data = {
            'channel_id': channel_id,
            'topic': topic,
            'privacy_level': privacy_level,
            'send_start_notification': send_start_notification,
            'guild_scheduled_event_id': guild_scheduled_event_id,
        }
        return cast(
            StageInstanceData,
            await self.request(
                'POST',
                Route(self, '/stage-instances'),
                data,
                reason=reason,
                t=StageInstanceData,
            )
        )

    async def get_stage_instance(
        self,
        channel_id: int,
    ) -> StageInstanceData:
        return cast(
            StageInstanceData,
            await self.request(
                'GET',
                Route(self, '/stage-instances/{channel_id}', channel_id=channel_id),
                t=StageInstanceData,
            )
        )

    async def modify_stage_instance(
        self,
        channel_id: int,
        *,
        topic: Maybe[str] = MISSING,
        privacy_level: Maybe[StageInstancePrivacyLevels] = MISSING,
        reason: str | None = None,
    ) -> StageInstanceData:
        data = {
            'topic': topic,
            'privacy_level': privacy_level,
        }
        return cast(
            StageInstanceData,
            await self.request(
                'PATCH',
                Route(self, '/stage-instances/{channel_id}', channel_id=channel_id),
                data,
                reason=reason,
                t=StageInstanceData,
            )
        )

    async def delete_stage_instance(
        self,
        channel_id: int,
        *,
        reason: str | None = None,
    ) -> StageInstanceData:
        return cast(
            StageInstanceData,
            await self.request(
                'DELETE',
                Route(self, '/stage-instances/{channel_id}', channel_id=channel_id),
                reason=reason,
                t=StageInstanceData,
            )
        )

    # Stickers
    async def get_sticker(
        self,
        sticker_id: int,
    ) -> StickerData:
        return cast(
            StickerData,
            await self.request(
                'GET',
                Route(self, '/stickers/{sticker_id}', sticker_id=sticker_id),
                t=StickerData,
            )
        )

    async def list_sticker_packs(
        self,
    ) -> list[StickerPackData]:
        return cast(
            list[StickerPackData],
            await self.request(
                'GET',
                Route(self, '/sticker-packs'),
                t=list[StickerPackData],
            )
        )

    async def list_guild_stickers(
        self,
        guild_id: int,
    ) -> list[StickerData]:
        return cast(
            list[StickerData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/stickers', guild_id=guild_id),
                t=list[StickerData],
            )
        )

    async def get_guild_sticker(
        self,
        guild_id: int,
        sticker_id: int,
    ) -> StickerData:
        return cast(
            StickerData,
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/stickers/{sticker_id}', guild_id=guild_id, sticker_id=sticker_id),
                t=StickerData,
            )
        )

    async def create_guild_sticker(
        self,
        guild_id: int,
        *,
        name: str,
        description: str,
        tags: str,
        file: File,
        reason: str | None = None,
    ) -> StickerData:
        data = [
            {"name": "name", "value": name},
            {"name": "description", "value": description},
            {"name": "tags", "value": tags},
            {
                "name": "file", "value": file.file.read(),
                "filename": file.filename, "content_type": "application/octet-stream"
            },
        ]
        return cast(
            StickerData,
            await self.request(
                'POST',
                Route(self, '/guilds/{guild_id}/stickers', guild_id=guild_id),
                form=data,
                files=[file],
                add_files=False,
                reason=reason,
                t=StickerData,
            )
        )

    async def modify_guild_sticker(
        self,
        guild_id: int,
        sticker_id: int,
        *,
        name: Maybe[str] = MISSING,
        description: Maybe[str | None] = MISSING,
        tags: Maybe[str] = MISSING,
        reason: str | None = None,
    ) -> StickerData:
        data = {
            'name': name,
            'description': description,
            'tags': tags,
        }
        return cast(
            StickerData,
            await self.request(
                'PATCH',
                Route(
                    self,
                    '/guilds/{guild_id}/stickers/{sticker_id}',
                    guild_id=guild_id,
                    sticker_id=sticker_id,
                ),
                remove_undefined(**data),
                reason=reason,
                t=StickerData,
            )
        )

    async def delete_guild_sticker(
        self,
        guild_id: int,
        sticker_id: int,
        *,
        reason: str | None = None,
    ) -> StickerData:
        return cast(
            StickerData,
            await self.request(
                'DELETE',
                Route(
                    self,
                    '/guilds/{guild_id}/stickers/{sticker_id}',
                    guild_id=guild_id,
                    sticker_id=sticker_id,
                ),
                reason=reason,
                t=StickerData,
            )
        )

    # Users
    async def get_current_user(
        self,
    ) -> UserData:
        return cast(
            UserData,
            await self.request(
                'GET',
                Route(self, '/users/@me'),
                t=UserData,
            )
        )

    async def get_user(
        self,
        user_id: int,
    ) -> UserData:
        return cast(
            UserData,
            await self.request(
                'GET',
                Route(self, '/users/{user_id}', user_id=user_id),
                t=UserData,
            )
        )

    async def modify_current_user(
        self,
        *,
        username: Maybe[str] = MISSING,
        avatar: Maybe[File | None] = MISSING,
    ) -> UserData:
        data = {
            'username': username,
            'avatar': to_datauri(avatar) if avatar else avatar,
        }
        return cast(
            UserData,
            await self.request(
                'PATCH',
                Route(self, '/users/@me'),
                remove_undefined(**data),
                t=UserData,
            )
        )

    async def get_current_user_guilds(
        self,
        *,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = 200,
        with_counts: Maybe[bool] = False,
    ) -> list[PartialGuildData]:
        path = form_qs(
            '/users/@me/guilds',
            before=before,
            after=after,
            limit=limit,
            with_counts=with_counts,
        )
        return cast(
            list[PartialGuildData],
            await self.request(
                'GET',
                Route(self, path),
                t=list[PartialGuildData],
            )
        )

    async def get_current_user_guild_member(
        self,
        guild_id: int,
    ) -> GuildMemberData:
        return cast(
            GuildMemberData,
            await self.request(
                'GET',
                Route(self, '/users/@me/guilds/{guild_id}', guild_id=guild_id),
                t=GuildMemberData,
            )
        )

    async def leave_guild(
        self,
        guild_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(self, '/users/@me/guilds/{guild_id}', guild_id=guild_id),
                t=None,
            )
        )

    async def create_dm(
        self,
        *,
        recipient_id: int,
    ) -> ChannelData:
        data = {
            'recipient_id': recipient_id,
        }
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(self, '/users/@me/channels'),
                data,
                t=ChannelData,
            )
        )

    async def create_group_dm(
        self,
        *,
        access_tokens: list[str],
        nicks: dict[int, str],
    ) -> ChannelData:
        data = {
            'access_tokens': access_tokens,
            'nicks': nicks,
        }
        return cast(
            ChannelData,
            await self.request(
                'POST',
                Route(self, '/users/@me/channels'),
                data,
                t=ChannelData,
            )
        )

    async def get_current_user_connections(
        self,
    ) -> list[ConnectionData]:
        return cast(
            list[ConnectionData],
            await self.request(
                'GET',
                Route(self, '/users/@me/connections'),
                t=list[ConnectionData],
            )
        )

    async def update_current_user_application_role_connection(
        self,
        application_id: int,
        access_token: str,
        *,
        platform_name: Maybe[str] = MISSING,
        platform_username: Maybe[str] = MISSING,
        metadata: Maybe[dict[str, int | datetime | bool]] = MISSING,
    ) -> ApplicationRoleConnectionData:
        data = {
            'platform_name': platform_name,
            'platform_username': platform_username,
            'metadata': metadata,
        }
        return cast(
            ApplicationRoleConnectionData,
            await self.request(
                'PUT',
                Route(self, '/users/@me/applications/{application_id}/role-connection', application_id=application_id),
                remove_undefined(**data),
                headers={"Authorization": "Bearer " + access_token},
                t=ApplicationRoleConnectionData,
            )
        )

    async def list_voice_regions(
        self,
    ) -> list[VoiceRegionData]:
        return cast(
            list[VoiceRegionData],
            await self.request(
                'GET',
                Route(self, '/voice/regions'),
                t=list[VoiceRegionData],
            )
        )

    # Webhooks
    async def create_webhook(
        self,
        channel_id: int,
        *,
        name: str,
        avatar: Maybe[File | None] = MISSING,
    ) -> WebhookData:
        data = {
            'name': name,
            'avatar': to_datauri(avatar) if avatar else avatar,
        }
        return cast(
            WebhookData,
            await self.request(
                'POST',
                Route(self, '/channels/{channel_id}/webhooks', channel_id=channel_id),
                remove_undefined(**data),
                t=WebhookData,
            )
        )

    async def get_channel_webhooks(
        self,
        channel_id: int,
    ) -> list[WebhookData]:
        return cast(
            list[WebhookData],
            await self.request(
                'GET',
                Route(self, '/channels/{channel_id}/webhooks', channel_id=channel_id),
                t=list[WebhookData],
            )
        )

    async def get_guild_webhooks(
        self,
        guild_id: int,
    ) -> list[WebhookData]:
        return cast(
            list[WebhookData],
            await self.request(
                'GET',
                Route(self, '/guilds/{guild_id}/webhooks', guild_id=guild_id),
                t=list[WebhookData],
            )
        )

    async def get_webhook(
        self,
        webhook_id: int,
    ) -> WebhookData:
        return cast(
            WebhookData,
            await self.request(
                'GET',
                Route(self, '/webhooks/{webhook_id}', webhook_id=webhook_id),
                t=WebhookData,
            )
        )

    async def get_webhook_with_token(
        self,
        webhook_id: int,
        webhook_token: str,
    ) -> WebhookData:
        return cast(
            WebhookData,
            await self.request(
                'GET',
                Route(
                    self, '/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id, webhook_token=webhook_token
                    ),
                t=WebhookData,
            )
        )

    async def modify_webhook(
        self,
        webhook_id: int,
        *,
        name: Maybe[str] = MISSING,
        avatar: Maybe[File | None] = MISSING,
        channel_id: Maybe[int] = MISSING,
    ) -> WebhookData:
        data = {
            'name': name,
            'avatar': to_datauri(avatar) if avatar else avatar,
            'channel_id': channel_id,
        }
        return cast(
            WebhookData,
            await self.request(
                'PATCH',
                Route(self, '/webhooks/{webhook_id}', webhook_id=webhook_id),
                remove_undefined(**data),
                t=WebhookData,
            )
        )

    async def modify_webhook_with_token(
        self,
        webhook_id: int,
        webhook_token: str,
        *,
        name: Maybe[str] = MISSING,
        avatar: Maybe[File | None] = MISSING,
    ) -> WebhookData:
        data = {
            'name': name,
            'avatar': to_datauri(avatar) if avatar else avatar,
        }
        return cast(
            WebhookData,
            await self.request(
                'PATCH',
                Route(
                    self, '/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id, webhook_token=webhook_token
                    ),
                remove_undefined(**data),
                t=WebhookData,
            )
        )

    async def delete_webhook(
        self,
        webhook_id: int,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(self, '/webhooks/{webhook_id}', webhook_id=webhook_id),
                t=None,
            )
        )

    async def delete_webhook_with_token(
        self,
        webhook_id: int,
        webhook_token: str,
    ) -> None:
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(
                    self, '/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id, webhook_token=webhook_token
                    ),
                t=None,
            )
        )

    async def execute_webhook(
        self,
        webhook_id: int,
        webhook_token: str,
        *,
        wait: Maybe[bool] = MISSING,
        thread_id: Maybe[int] = MISSING,
        content: Maybe[str] = MISSING,
        username: Maybe[str] = MISSING,
        avatar_url: Maybe[str] = MISSING,
        tts: Maybe[bool] = MISSING,
        embeds: Maybe[list[EmbedData]] = MISSING,
        allowed_mentions: Maybe[AllowedMentionsData] = MISSING,
        components: Maybe[list[ComponentData]] = MISSING,
        files: Maybe[list[File]] = MISSING,
        attachments: Maybe[list[PartialAttachmentData]] = MISSING,
        flags: Maybe[int] = MISSING,
        thread_name: Maybe[str] = MISSING,
        applied_tags: Maybe[list[int]] = MISSING,
    ) -> MessageData:
        path = form_qs(
            '/webhooks/{webhook_id}/{webhook_token}',
            wait=wait,
            thread_id=thread_id,
        )
        data = remove_undefined(
            content=content,
            username=username,
            avatar_url=avatar_url,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            attachments=attachments,
            flags=flags,
            thread_name=thread_name,
            applied_tags=applied_tags,
        )
        return cast(
            MessageData,
            await self.request(
                'POST',
                Route(self, path, webhook_id=webhook_id, webhook_token=webhook_token),
                data,
                files=files,
                t=MessageData,
            )
        )

    async def get_webhook_message(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int,
        *,
        thread_id: Maybe[int] = MISSING,
    ) -> MessageData:
        path = form_qs(
            '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
            thread_id=thread_id,
        )
        return cast(
            MessageData,
            await self.request(
                'GET',
                Route(self, path, webhook_id=webhook_id, webhook_token=webhook_token, message_id=message_id),
                t=MessageData,
            )
        )

    async def edit_webhook_message(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int,
        *,
        thread_id: Maybe[int] = MISSING,
        content: Maybe[str | None] = MISSING,
        embeds: Maybe[list[EmbedData] | None] = MISSING,
        allowed_mentions: Maybe[AllowedMentionsData | None] = MISSING,
        components: Maybe[list[ComponentData] | None] = MISSING,
        files: Maybe[list[File] | None] = MISSING,
        attachments: Maybe[list[PartialAttachmentData] | None] = MISSING,
    ) -> MessageData:
        path = form_qs(
            '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
            thread_id=thread_id,
        )
        data = remove_undefined(
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            attachments=attachments,
        )
        return cast(
            MessageData,
            await self.request(
                'PATCH',
                Route(self, path, webhook_id=webhook_id, webhook_token=webhook_token, message_id=message_id),
                data,
                files=files,
                t=MessageData,
            )
        )

    async def delete_webhook_message(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int,
        *,
        thread_id: int,
    ) -> None:
        path = form_qs(
            '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
            thread_id=thread_id,
        )
        return cast(
            None,
            await self.request(
                'DELETE',
                Route(self, path, webhook_id=webhook_id, webhook_token=webhook_token, message_id=message_id),
                t=None,
            )
        )
