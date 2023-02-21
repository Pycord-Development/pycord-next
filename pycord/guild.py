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

import datetime
from typing import Any, TYPE_CHECKING

from .pages.paginator import Page, Paginator
from .auto_moderation import (
    AutoModAction,
    AutoModEventType,
    AutoModRule,
    AutoModTriggerMetadata,
    AutoModTriggerType,
)
from .channel import (
    _Overwrite,
    AnnouncementThread, CategoryChannel,
    Channel,
    CHANNEL_TYPE,
    ForumTag,
    identify_channel,
    TextChannel,
    Thread, VoiceChannel,
)
from .enums import (
    ChannelType,
    DefaultMessageNotificationLevel,
    ExplicitContentFilterLevel,
    MFALevel,
    NSFWLevel,
    PremiumTier,
    SortOrderType,
    VerificationLevel,
    VideoQualityMode,
)
from .flags import Permissions, SystemChannelFlags
from .media import Emoji, Sticker
from .member import Member, MemberPaginator
from .role import Role
from .snowflake import Snowflake
from .types import (
    Ban as DiscordBan,
    Guild as DiscordGuild,
    GUILD_FEATURE,
    GuildPreview as DiscordGuildPreview,
    LOCALE,
    UnavailableGuild,
    Widget as DiscordWidget,
    WidgetSettings as DiscordWidgetSettings,
)
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .utils import remove_undefined
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    from .state import State


class ChannelPosition:
    def __init__(
        self,
        id: Snowflake,
        position: int, *,
        lock_permissions: bool = False,
        parent_id: Snowflake | None | UndefinedType
    ) -> None:
        self.id = id
        self.position = position
        self.lock_permissions = lock_permissions
        self.parent_id = parent_id

    def to_dict(self) -> dict[str, Any]:
        payload = {
            'id': self.id,
            'position': self.position,
            'lock_permissions': self.lock_permissions,
            'parent_id': self.parent_id
        }
        return remove_undefined(**payload)


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

    async def list_auto_moderation_rules(self) -> list[AutoModRule]:
        """list the auto moderation rules for this guild.
        
        Returns
        -------
        list[:class:`AutoModRule`]
            The auto moderation rules for this guild.
        """
        data = await self._state.http.list_auto_moderation_rules_for_guild(self.id)
        return [AutoModRule(rule, self._state) for rule in data]
    
    async def get_auto_moderation_rule(self, rule_id: int) -> AutoModRule:
        """Get an auto moderation rule for this guild.
        
        Parameters
        ----------
        rule_id: :class:`int`
            The ID of the rule to get.
        
        Returns
        -------
        :class:`AutoModRule`
            The auto moderation rule for this guild.
        """
        data = await self._state.http.get_auto_moderation_rule_for_guild(self.id, rule_id)
        return AutoModRule(data, self._state)

    async def create_auto_moderation_rule(
        self, *,
        name: str,
        event_type: AutoModEventType,
        trigger_type: AutoModTriggerType,
        trigger_metadata: AutoModTriggerMetadata | UndefinedType = UNDEFINED,
        actions: list[AutoModAction],
        enabled: bool = False,
        exempt_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        exempt_channels: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> AutoModRule:
        """Create an auto moderation rule for this guild.

        Parameters
        ----------
        name: :class:`str`
            The name of the rule.
        event_type: :class:`AutoModEventType`
            The event type of the rule.
        trigger_type: :class:`AutoModTriggerType`
            The trigger type of the rule.
        trigger_metadata: :class:`AutoModTriggerMetadata`
            The trigger metadata of the rule.
        actions: list[:class:`AutoModAction`]
            The actions to take when the rule is triggered.
        enabled: :class:`bool`
            Whether the rule is enabled.
        exempt_roles: list[:class:`Snowflake`]
            The roles to exempt from this rule.
        exempt_channels: list[:class:`Snowflake`]
            The channels to exempt from this rule.
        reason: :class:`str` | None
            The reason for creating the rule.

        Returns
        -------
        :class:`AutoModRule`
            The auto moderation rule for this guild.
        """
        data = await self._state.http.create_auto_moderation_rule_for_guild(
            self.id,
            name=name,
            event_type=event_type,
            trigger_type=trigger_type,
            trigger_metadata=trigger_metadata,
            actions=actions,
            enabled=enabled,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason,
        )
        return AutoModRule(data, self._state)

    async def create_emoji(
        self, *,
        name: str,
        image: bytes,  # TODO
        roles: list[Role] | None = None,
        reason: str | None = None
    ) -> Emoji:
        """Creates an emoji.

        Parameters
        ----------
        name: :class:`str`
            The name of the emoji.
        image: :class:`bytes`
            The image data of the emoji.
        roles: list[:class:`Role`]
            The roles that can use the emoji.
        reason: :class:`str` | None
            The reason for creating the emoji. Shows up on the audit log.

        Returns
        -------
        :class:`Emoji`
            The created emoji.
        """
        data = await self._state.http.create_guild_emoji(
            self.id, name, image, roles, reason
        )
        return Emoji(data, state=self._state)

    async def edit_emoji(
        self, emoji_id: Snowflake, *,
        name: str | UndefinedType = UNDEFINED,
        roles: list[Role] | UndefinedType = UNDEFINED,
        reason: str | None = None
    ) -> Emoji:
        """Edits the emoji.

        Parameters
        ----------
        emoji_id: :class:`Snowflake`
            The ID of the emoji to edit.
        name: :class:`str`
            The new name of the emoji.
        roles: list[:class:`Role`]
            The new roles that can use the emoji.
        reason: :class:`str` | None
            The reason for editing the emoji. Shows up on the audit log.

        Returns
        -------
        :class:`Emoji`
            The edited emoji.
        """
        data = await self._state.http.modify_guild_emoji(
            self.id, emoji_id, name=name, roles=roles, reason=reason
        )
        return Emoji(data, self._state)

    async def delete_emoji(self, emoji_id: Snowflake, *, reason: str | None = None) -> None:
        """Deletes an emoji.

        Parameters
        ----------
        emoji_id: :class:`Snowflake`
            The ID of the emoji to delete.
        reason: :class:`str` | None
            The reason for deleting the emoji. Shows up on the audit log.
        """
        await self._state.http.delete_guild_emoji(self.id, emoji_id, reason=reason)

    async def get_preview(self) -> GuildPreview:
        """Get a preview of this guild.

        Returns
        -------
        :class:`GuildPreview`
            The preview of this guild.
        """
        data = await self._state.http.get_guild_preview(self.id)
        return GuildPreview(data, self._state)
    
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        verification_level: VerificationLevel | None | UndefinedType = UNDEFINED,
        default_message_notifications: DefaultMessageNotificationLevel | None | UndefinedType = UNDEFINED,
        explicit_content_filter: ExplicitContentFilterLevel | None | UndefinedType = UNDEFINED,
        afk_channel: VoiceChannel | None | UndefinedType = UNDEFINED,
        afk_timeout: int | UndefinedType = UNDEFINED,
        icon: bytes | None | UndefinedType = UNDEFINED,  # TODO
        owner: User | UndefinedType = UNDEFINED,
        splash: bytes | None | UndefinedType = UNDEFINED,  # TODO
        discovery_splash: bytes | None | UndefinedType = UNDEFINED,  # TODO
        banner: bytes | None | UndefinedType = UNDEFINED,  # TODO
        system_channel: TextChannel | None | UndefinedType = UNDEFINED,
        rules_channel: TextChannel | None | UndefinedType = UNDEFINED,
        public_updates_channel: TextChannel | None | UndefinedType = UNDEFINED,
        preferred_locale: str | None | UndefinedType = UNDEFINED,
        features: list[GUILD_FEATURE] | UndefinedType = UNDEFINED,
        description: str | None | UndefinedType = UNDEFINED,
        premium_progress_bar_enabled: bool | UndefinedType = UNDEFINED,
        reason: str | None = None
    ) -> Guild:
        """Edits the guild.
        
        Parameters
        ----------
        name: :class:`str`
            The new name of the guild.
        verification_level: :class:`VerificationLevel`
            The new verification level of the guild.
        default_message_notifications: :class:`DefaultMessageNotificationLevel`
            The new default message notification level of the guild.
        explicit_content_filter: :class:`ExplicitContentFilterLevel`
            The new explicit content filter level of the guild.
        afk_channel: :class:`VoiceChannel`
            The new AFK channel of the guild.
        afk_timeout: :class:`int`
            The new AFK timeout of the guild.
        icon: :class:`bytes`
            The new icon of the guild.
        owner: :class:`User`
            The new owner of the guild.
        splash: :class:`bytes`
            The new splash of the guild.
        discovery_splash: :class:`bytes`
            The new discovery splash of the guild.
        banner: :class:`bytes`
            The new banner of the guild.
        system_channel: :class:`TextChannel`
            The new system channel of the guild.
        rules_channel: :class:`TextChannel`
            The new rules channel of the guild.
        public_updates_channel: :class:`TextChannel`
            The new public updates channel of the guild.
        preferred_locale: :class:`str`
            The new preferred locale of the guild.
        features: list[:class:`GUILD_FEATURE`]
            The new features of the guild.
        description: :class:`str`
            The new description of the guild.
        reason: :class:`str` | None
            The reason for editing the guild. Shows up on the audit log.
        premium_progress_bar_enabled: :class:`bool`
            Whether the premium progress bar is enabled.
            
        Returns
        -------
        :class:`Guild`
            The edited guild.
        """
        data = await self._state.http.modify_guild(
            self.id,
            name=name,
            verification_level=verification_level.value if verification_level else verification_level,
            default_message_notifications=default_message_notifications.value if default_message_notifications else default_message_notifications,
            explicit_content_filter=explicit_content_filter.value if explicit_content_filter else explicit_content_filter,
            afk_channel_id=afk_channel.id if afk_channel else afk_channel,
            afk_timeout=afk_timeout,
            icon=icon,
            owner_id=owner.id if owner else owner,
            splash=splash,
            discovery_splash=discovery_splash,
            banner=banner,
            system_channel_id=system_channel.id if system_channel else system_channel,
            rules_channel_id=rules_channel.id if rules_channel else rules_channel,
            public_updates_channel_id=public_updates_channel.id if public_updates_channel else public_updates_channel,
            preferred_locale=preferred_locale,
            features=features,
            description=description,
            premium_progress_bar_enabled=premium_progress_bar_enabled,
            reason=reason,
        )
        return Guild(data, self._state)

    async def delete(self) -> None:
        """Deletes the guild."""
        await self._state.http.delete_guild(self.id)

    async def get_channels(self) -> list[CHANNEL_TYPE]:
        """Gets the channels of the guild.

        Returns
        -------
        list[:class:`Channel`]
            The channels of the guild.
        """
        data = await self._state.http.get_guild_channels(self.id)
        return [identify_channel(channel, self._state) for channel in data]

    async def create_channel(
        self, name: str, type: ChannelType, *,
        topic: str | None | UndefinedType = UNDEFINED,
        bitrate: int | None | UndefinedType = UNDEFINED,
        user_limit: int | None | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | None | UndefinedType = UNDEFINED,
        parent: CategoryChannel | None | UndefinedType = UNDEFINED,
        nsfw: bool | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: VideoQualityMode | None | UndefinedType = UNDEFINED,
        default_auto_archive_duration: int | None | UndefinedType = UNDEFINED,
        default_reaction_emoji: str | None | UndefinedType = UNDEFINED,
        available_tags: list[ForumTag] | None | UndefinedType = UNDEFINED,
        default_sort_order: SortOrderType | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> CHANNEL_TYPE:
        """Creates a channel in the guild.

        Parameters
        ----------
        name: :class:`str`
            The name of the channel.
        type: :class:`ChannelType`
            The type of the channel.
        topic: :class:`str` | None | :attr:`UNDEFINED`
            The topic of the channel.
        bitrate: :class:`int` | None | :attr:`UNDEFINED`
            The bitrate of the channel.
        user_limit: :class:`int` | None | :attr:`UNDEFINED`
            The user limit of the channel.
        rate_limit_per_user: :class:`int` | None | :attr:`UNDEFINED`
            The rate limit per user of the channel.
        position: :class:`int` | None | :attr:`UNDEFINED`
            The position of the channel.
        permission_overwrites: list[:class:`_Overwrite`]
            The permission overwrites of the channel.
        parent: :class:`CategoryChannel` | None | :attr:`UNDEFINED`
            The parent of the channel.
        nsfw: :class:`bool` | :attr:`UNDEFINED`
            Whether the channel is NSFW.
        rtc_region: :class:`str` | None | :attr:`UNDEFINED`
            The RTC region of the channel.
        video_quality_mode: :class:`VideoQualityMode` | None | :attr:`UNDEFINED`
            The video quality mode of the channel.
        default_auto_archive_duration: :class:`int` | None | :attr:`UNDEFINED`
            The default auto archive duration of the channel.
        default_reaction_emoji: :class:`str` | None | :attr:`UNDEFINED`
            The default reaction emoji of the channel.
        available_tags: list[:class:`ForumTag`] | None | :attr:`UNDEFINED`
            The available tags of the channel.
        default_sort_order: :class:`SortOrderType` | None | :attr:`UNDEFINED`
            The default sort order of the channel.
        reason: :class:`str` | None
            The reason for creating the channel. Shows up on the audit log.

        Returns
        -------
        :class:`Channel`
            The created channel.
        """
        data = await self._state.http.create_channel(
            self.id,
            name=name,
            type=type.value if type else type,
            topic=topic,
            bitrate=bitrate,
            user_limit=user_limit,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            permission_overwrites=[o.to_dict() for o in permission_overwrites],
            parent_id=parent.id if parent else parent,
            nsfw=nsfw,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            default_auto_archive_duration=default_auto_archive_duration,
            default_reaction_emoji=default_reaction_emoji,
            available_tags=available_tags,
            default_sort_order=default_sort_order,
            reason=reason,
        )
        return identify_channel(data, self._state)

    async def modify_channel_positions(
        self, channels: list[ChannelPosition]
    ) -> None:
        """Modifies the positions of the channels.

        Parameters
        ----------
        channels: list[:class:`ChannelPosition`]
            The channels to modify.
        """
        await self._state.http.modify_channel_positions(
            self.id, [c.to_dict() for c in channels]
        )

    async def list_active_threads(self) -> list[Thread | AnnouncementThread]:
        """Lists the active threads in the guild.

        Returns
        -------
        list[:class:`Channel`]
            The active threads in the guild.
        """
        data = await self._state.http.list_active_threads(self.id)
        return [identify_channel(channel, self._state) for channel in data]

    async def get_member(self, id: Snowflake):
        """Gets a member from the guild.

        Parameters
        ----------
        id: :class:`Snowflake`
            The ID of the member.

        Returns
        -------
        :class:`Member`
            The member.
        """
        data = await self._state.http.get_member(self.id, id)
        return Member(data, self._state, guild_id=self.id)

    def list_members(self, limit: int = None, after: datetime.datetime | None = None) -> MemberPaginator:
        """Lists the members in the guild.

        Parameters
        ----------
        limit: :class:`int`
            The maximum number of members to return.
        after: :class:`datetime.datetime` | None
            List only members whos accounts were created after this date.

        Returns
        -------
        :class:`MemberPaginator`
            An async iterator that can be used for iterating over the guild's members.
        """
        return MemberPaginator(self._state, self.id, limit=limit, after=after)

    async def search_members(
        self,
        query: str, *,
        limit: int = None,
    ) -> list[Member]:
        """Searches for members in the guild.

        Parameters
        ----------
        query: :class:`str`
            The query to search for.
        limit: :class:`int`
            The maximum number of members to return.

        Returns
        -------
        list[:class:`Member`]
            The members.
        """
        data = await self._state.http.search_guild_members(self.id, query, limit=limit)
        return [Member(member, self._state, guild_id=self.id) for member in data]

    async def add_member(
        self,
        id: Snowflake,
        access_token: str,
        *,
        nick: str | None = None,
        roles: list[Role] | None = None,
        mute: bool = False,
        deaf: bool = False,
    ) -> Member:
        """Adds a member to the guild through Oauth2.

        Parameters
        ----------
        id: :class:`Snowflake`
            The ID of the member.
        access_token: :class:`str`
            The access token of the member.
        nick: :class:`str` | None
            The nickname of the member.
        roles: list[:class:`Role`] | None
            The roles of the member.
        mute: :class:`bool`
            Whether the member is muted.
        deaf: :class:`bool`
            Whether the member is deafened.

        Returns
        -------
        :class:`Member`
            The member.
        """
        nick = nick or UNDEFINED
        roles = roles or []
        data = await self._state.http.add_member(
            self.id,
            id,
            access_token,
            nick=nick,
            roles=[role.id for role in roles],
            mute=mute,
            deaf=deaf,
        )
        return Member(data, self._state, guild_id=self.id)

    async def edit_own_member(
        self, *,
        nick: str | None | UndefinedType = UNDEFINED,
        reason: str | None = None
    ) -> Member:
        """Edits the bot's guild member.

        Parameters
        ----------
        nick: :class:`str` | None | :class:`UndefinedType`
            The bot's new nickname.
        reason: :class:`str` | None
            The reasoning for editing the bot. Shows up in the audit log.

        Returns
        -------
        :class:`Member`
            The updated member.
        """
        data = await self._state.http.modify_current_member(
            self.id,
            nick=nick,
            reason=reason
        )
        return Member(data, self._state, guild_id=self.id)

    def get_bans(
        self, *,
        limit: int | None = 1000,
        before: datetime.datetime | None = None,
        after: datetime.datetime | None = None,
    ) -> BanPaginator:
        """Lists the bans in the guild.

        .. note::
           If both ``after`` and ``before`` parameters are provided,
           only ``before`` will be respected.

        Parameters
        ----------
        limit: :class:`int`
            The maximum number of bans to return.
        before: :class:`datetime.datetime` | None
            List only bans related to users whos accounts
            were created before this date.
            This is not related to the ban's creation date.
        after: :class:`datetime.datetime` | None
            List only bans related to users whos accounts
            were created after this date.
            This is not related to the ban's creation date.

        Returns
        -------
        :class:`BanPaginator`
            An async iterator that can be used for iterating over the guild's bans.
        """
        return BanPaginator(self._state, self.id, limit=limit, before=before, after=after)

    async def get_ban(
        self, user_id: Snowflake,
    ) -> Ban:
        """Gets a ban for a user.

        Parameters
        ----------
        user_id: :class:`Snowflake`
            The user ID to fetch a ban for.

        Returns
        -------
        :class:`Ban`
            The user's ban.
        """
        data = await self._state.http.get_guild_ban(self.id, user_id)
        return Ban(data, self._state)

    async def ban(
        self,
        user: User, *,
        delete_message_seconds: int | UndefinedType = UNDEFINED,
        reason: str | None = None
    ) -> None:
        """Bans a user.

        Parameters
        ----------
        user: :class:`User`
            The user to ban
        delete_message_seconds: :class:`int` | UndefinedType
            The amount of seconds worth of messages that should be deleted.
        reason: :class:`str` | None
            The reason for the ban. Shows up in the audit log, and when the ban is fetched.
        """
        await self._state.http.create_guild_ban(
            self.id, user.id,
            delete_message_seconds=delete_message_seconds,
            reason=reason
        )

    async def unban(
        self,
        user: User, *,
        reason: str | None = None
    ) -> None:
        """Unbans a user.

        Parameters
        ----------
        user: :class:`User`
            The user to unban
        reason: :class:`str` | None
            The reason for the unban. Shows up in the audit log.
        """
        await self._state.http.remove_guild_ban(
            self.id, user.id,
            reason=reason
        )


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


class BanPage(Page[Ban]):
    def __init__(self, ban: Ban) -> None:
        self.value = ban


class BanPaginator(Paginator[BanPage]):
    def __init__(
        self,
        state: State,
        guild_id: Snowflake,
        *,
        limit: int = 1,
        before: datetime.datetime | None = None,
        after: datetime.datetime | None = None,
    ) -> None:
        super().__init__()
        self._state: State = state
        self.guild_id: Snowflake = guild_id
        self.limit: int | None = limit
        self.reverse_order: bool = False
        self.last_id: Snowflake | UndefinedType
        if before:
            self.last_id = Snowflake.from_datetime(before)
            self.reverse_order = True
        elif after:
            self.last_id = Snowflake.from_datetime(after)
        else:
            self.last_id = UNDEFINED
        self.done = False

    async def fill(self):
        if self._previous_page is None or self._previous_page[0] >= len(self._pages):
            if self.done:
                raise StopAsyncIteration
            limit = min(self.limit, 1000) if self.limit else 1000
            if self.limit is not None:
                self.limit -= limit
            if self.reverse_order:
                param = {'before': self.last_id}
            else:
                param = {'after': self.last_id}
            data = await self._state.http.get_guild_bans(
                self.guild_id,
                limit=limit,
                **param,
            )
            if len(data) < limit or self.limit <= 0:
                self.done = True
            if not data:
                raise StopAsyncIteration
            if self.reverse_order:
                data.reverse()
            for member in data:
                self.add_page(
                    BanPage(
                        Ban(
                            member,
                            self._state,
                        )
                    )
                )

    async def forward(self):
        await self.fill()
        value = await super().forward()
        self.last_id = value.user.id
        return value
