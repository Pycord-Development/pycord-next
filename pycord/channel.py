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

from datetime import datetime
from typing import Any, TYPE_CHECKING

from .embed import Embed
from .enums import ChannelType, OverwriteType, VideoQualityMode
from .errors import ComponentException
from .flags import ChannelFlags, Permissions
from .member import Member
from .message import AllowedMentions, Message, MessageReference
from .snowflake import Snowflake
from .types import (
    Channel as DiscordChannel,
    DefaultReaction as DiscordDefaultReaction,
    ForumTag as DiscordForumTag,
    Overwrite as DiscordOverwrite,
    ThreadMember as DiscordThreadMember,
    ThreadMetadata as DiscordThreadMetadata,
)
from .undefined import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State
    from .ui.house import House


class _Overwrite:
    def __init__(
        self,
        id: int,
        type: OverwriteType,
        *,
        allow: Permissions,
        deny: Permissions,
    ) -> None:
        self.id: Snowflake = Snowflake(id)
        self.type: OverwriteType = type
        self.allow: Permissions = allow
        self.deny: Permissions = deny

    @classmethod
    def from_dict(cls, overwrite: DiscordOverwrite) -> _Overwrite:
        return cls(
            int(overwrite['id']),
            OverwriteType(overwrite['type']),
            allow=Permissions.from_value(overwrite['allow']),
            deny=Permissions.from_value(overwrite['deny']),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'allow': self.allow.value,
            'deny': self.deny.value,
        }


class ThreadMetadata:
    def __init__(self, metadata: DiscordThreadMetadata) -> None:
        self.archived: bool = metadata['archived']
        self.auto_archive_duration: int = metadata['auto_archive_duration']
        self.archive_timestamp: datetime = datetime.fromisoformat(
            metadata['archive_timestamp']
        )
        self.locked: bool = metadata['locked']
        self.invitable: bool | UndefinedType = metadata.get('invitable', UNDEFINED)
        self.create_timestamp: datetime | UndefinedType = (
            datetime.fromisoformat(metadata.get('create_timestamp'))
            if metadata.get('create_timestamp') is not None
            else UNDEFINED
        )


class ThreadMember:
    def __init__(self, member: DiscordThreadMember) -> None:
        self._id: str | None = member.get('id')
        self.id: Snowflake | UndefinedType = (
            Snowflake(self._id) if self._id is not None else UNDEFINED
        )
        self._user_id: str | None = member.get('user_id')
        self.user_id: Snowflake | UndefinedType = (
            Snowflake(self._user_id) if self._user_id is not None else UNDEFINED
        )
        self.join_timestamp: datetime = datetime.fromisoformat(member['join_timestamp'])
        self.flags: int = member['flags']
        self.member: Member | None = Member(member['member']) if 'member' in member else None


class ForumTag:
    def __init__(
        self, *,
        name: str,
        moderated: bool = False,
        emoji_id: Snowflake | str | None = None,
        emoji_name: str | None = None,
    ) -> None:
        self.id: Snowflake | None = None
        self.name: str = name
        self.moderated: bool = moderated
        self.emoji_id: Snowflake | str = emoji_id
        self.emoji_name: str | None = emoji_name

    @classmethod
    def from_dict(cls, data: DiscordForumTag) -> ForumTag:
        obj = cls(
            name=data['name'],
            moderated=data['moderated'],
            emoji_id=Snowflake(em_id) if isinstance(em_id := data.get('emoji_id'), int) else em_id,
            emoji_name=data.get('emoji_name'),
        )
        obj.id = Snowflake(data['id'])
        return obj

    def to_dict(self) -> dict[str, Any]:
        # omit ID because we don't send that to Discord
        return {
            'name': self.name,
            'moderated': self.moderated,
            'emoji_id': self.emoji_id,
            'emoji_name': self.emoji_name,
        }


class DefaultReaction:
    def __init__(self, data: DiscordDefaultReaction) -> None:
        self._emoji_id: str | None = data.get('emoji_id')
        self.emoji_id: Snowflake | None = (
            Snowflake(self._emoji_id) if self._emoji_id is not None else None
        )
        self.emoji_name: str | None = data['emoji_name']


class FollowedChannel:
    def __init__(self, data: dict[str, Any]) -> None:
        self.channel_id: Snowflake = Snowflake(data['channel_id'])
        self.webhook_id: Snowflake = Snowflake(data['webhook_id'])


class Channel:
    """
    Represents a Discord channel. All other channel types inherit from this.

    Attributes
    ----------
    id: :class:`Snowflake`
        The ID of the channel.
    type: :class:`ChannelType`
        The type of the channel.
    name: :class:`str` | :class:`UndefinedType`
        The name of the channel.
    flags: :class:`ChannelFlags` | :class:`UndefinedType`
        The flags of the channel.
    """

    def __init__(self, data: DiscordChannel, state: State) -> None:
        self._state = state
        self.id: Snowflake = Snowflake(data['id'])
        self.type: ChannelType = ChannelType(data['type'])
        self.name: str | UndefinedType = data.get('name', UNDEFINED)
        self.flags: ChannelFlags | UndefinedType = (
            ChannelFlags.from_value(data['flags'])
            if data.get('flags') is not None
            else UNDEFINED
        )

    async def _base_edit(self, **kwargs: Any) -> Channel:
        data = await self._state.http.modify_channel(self.id, **kwargs)
        return self.__class__(data, self._state)

    async def delete(self, reason: str | None = None) -> None:
        """
        Delete this channel.

        Parameters
        ----------
        reason: :class:`str` | None
            The reason for deleting this channel. Shows up on the audit log.
        """
        await self._state.http.delete_channel(self.id, reason=reason)


class GuildChannel(Channel):
    """
    Represents a Discord guild channel. All other guild channel types inherit from this.

    Attributes
    ----------
    id: :class:`Snowflake`
        The ID of the channel.
    type: :class:`ChannelType`
        The type of the channel.
    name: :class:`str` | :class:`UndefinedType`
        The name of the channel.
    flags: :class:`ChannelFlags` | :class:`UndefinedType`
        The flags of the channel.
    guild_id: :class:`Snowflake` | :class:`UndefinedType`
        The ID of the guild this channel belongs to.
    position: :class:`int` | :class:`UndefinedType`
        The position of the channel.
    permission_overwrites: list[:class:`_Overwrite`]
        The permission overwrites of the channel.
    topic: :class:`str` | None | :class:`UndefinedType`
        The topic of the channel.
    nsfw: :class:`bool` | :class:`UndefinedType`
        Whether the channel is NSFW.
    permissions: :class:`Permissions` | :class:`UndefinedType`
        The bot's permissions in this channel.
    parent_id: :class:`Snowflake` | None | :class:`UndefinedType`
        The ID of the parent category of this channel.
    rate_limit_per_user: :class:`int` | :class:`UndefinedType`
        The slowmode rate limit of the channel.
    default_auto_archive_duration: :class:`int` | :class:`UndefinedType`
        The default auto archive duration of the channel.
    """

    def __init__(self, data: DiscordChannel, state: State) -> None:
        super().__init__(data, state)
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data['guild_id'])
            if data.get('guild_id') is not None
            else UNDEFINED
        )
        self.position: int | UndefinedType = data.get('position', UNDEFINED)
        self.permission_overwrites: list[_Overwrite] = [
            _Overwrite.from_dict(d) for d in data.get('permission_overwrites', [])
        ]
        self.topic: str | None | UndefinedType = data.get('topic', UNDEFINED)
        self.nsfw: bool | UndefinedType = data.get('nsfw', UNDEFINED)
        self.permissions: Permissions | UndefinedType = (
            Permissions.from_value(data['permissions'])
            if data.get('permissions') is not None
            else UNDEFINED
        )
        self.parent_id: Snowflake | UndefinedType = (
            Snowflake(data['parent_id'])
            if data.get('parent_id') is not None
            else data.get('parent_id', UNDEFINED)
        )
        self.rate_limit_per_user: int | UndefinedType = data.get(
            'rate_limit_per_user', UNDEFINED
        )
        self.default_auto_archive_duration: int | UndefinedType = data.get(
            'default_auto_archive_duration', UNDEFINED
        )


class MessageableChannel(Channel):
    def __init__(self, data: DiscordChannel, state: State) -> None:
        super().__init__(data, state)
        self.last_message_id: int | None = (
            Snowflake(data['last_message_id'])
            if data.get('last_message_id') is not None
            else None
        )
        self.last_pin_timestamp: None | datetime | UndefinedType = (
            datetime.fromisoformat(data['last_pin_timestamp'])
            if data.get('last_pin_timestamp') is not None
            else data.get('last_pin_timestamp', UNDEFINED)
        )

    async def send(
        self,
        content: str | UndefinedType = UNDEFINED,
        nonce: int | str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentions | UndefinedType = UNDEFINED,
        message_reference: MessageReference | UndefinedType = UNDEFINED,
        sticker_ids: list[Snowflake] | UndefinedType = UNDEFINED,
        flags: int | UndefinedType = UNDEFINED,
        house: House | UndefinedType = UNDEFINED,
        houses: list[House] | UndefinedType = UNDEFINED,
    ) -> Message:
        if house and houses:
            houses.append(house)

        if houses:
            if len(houses) > 5:
                raise ComponentException('Cannot have over five houses at once')

            components = [(house.action_row())._to_dict() for house in houses]

            for house in houses:
                self._state.sent_house(house)
        elif house:
            components = [(house.action_row())._to_dict()]
            self._state.sent_house(house)
        else:
            components = UNDEFINED

        data = await self._state.http.create_message(
            channel_id=self.id,
            content=content,
            nonce=nonce,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions.to_dict() if allowed_mentions else UNDEFINED,
            message_reference=message_reference.to_dict() if message_reference else UNDEFINED,
            sticker_ids=sticker_ids,
            flags=flags,
            components=components,
        )
        return Message(data, state=self._state)

    async def trigger_typing(self) -> None:
        await self._state.http.trigger_typing_indicator(self.id)

    async def bulk_delete(self, *messages: Message, reason: str | None = None) -> None:
        await self._state.http.bulk_delete_messages(self.id, [m.id for m in messages], reason=reason)


class AudioChannel(GuildChannel):
    def __init__(self, data: DiscordChannel, state: State) -> None:
        super().__init__(data, state)
        self.rtc_region: str | UndefinedType = data.get('rtc_region', UNDEFINED)
        self.video_quality_mode: VideoQualityMode | UndefinedType = (
            VideoQualityMode(data['video_quality_mode'])
            if data.get('video_quality_mode') is not None
            else UNDEFINED
        )
        self.bitrate: int | UndefinedType = data.get('bitrate', UNDEFINED)
        self.user_limit: int | UndefinedType = data.get('user_limit', UNDEFINED)


class TextChannel(MessageableChannel, GuildChannel):
    # Type 0
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        type: ChannelType | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        topic: str | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | UndefinedType = UNDEFINED,
        parent_id: Snowflake | None | UndefinedType = UNDEFINED,
        default_auto_archive_duration: int | None | UndefinedType = UNDEFINED,
        default_thread_rate_limit_per_user: int | UndefinedType = UNDEFINED,
    ) -> TextChannel:
        return await self._base_edit(
            name=name,
            type=type.value if type else UNDEFINED,
            position=position,
            topic=topic,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            permission_overwrites=[o.to_dict() for o in permission_overwrites] if permission_overwrites else UNDEFINED,
            parent_id=parent_id,
            default_auto_archive_duration=default_auto_archive_duration,
            default_thread_rate_limit_per_user=default_thread_rate_limit_per_user,
        )

    async def get_pinned_messages(self) -> list[Message]:
        data = await self._state.http.get_pinned_messages(self.id)
        return [Message(m, state=self._state) for m in data]

    async def create_thread(
        self,
        name: str,
        auto_archive_duration: int | UndefinedType = UNDEFINED,
        type: ChannelType = ChannelType.PUBLIC_THREAD,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Thread | AnnouncementThread:
        data = await self._state.http.start_thread_without_message(
            self.id,
            name=name,
            auto_archive_duration=auto_archive_duration,
            type=type.value,
            invitable=invitable,
            rate_limit_per_user=rate_limit_per_user,
            reason=reason,
        )
        return identify_channel(data, state=self._state)

    async def list_public_archived_threads(
        self,
        before: datetime.datetime | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
    ) -> list[Thread]:
        data = await self._state.http.list_public_archived_threads(
            self.id,
            before=before.isoformat() if before else UNDEFINED,
            limit=limit,
        )
        return [Thread(d, state=self._state) for d in data]

    async def list_private_archived_threads(
        self,
        before: datetime.datetime | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
    ) -> list[Thread]:
        data = await self._state.http.list_private_archived_threads(
            self.id,
            before=before.isoformat() if before else UNDEFINED,
            limit=limit,
        )
        return [Thread(d, state=self._state) for d in data]

    async def list_joined_private_archived_threads(
        self,
        before: datetime.datetime | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
    ) -> list[Thread]:
        data = await self._state.http.list_joined_private_archived_threads(
            self.id,
            before=before.isoformat() if before else UNDEFINED,
            limit=limit,
        )
        return [Thread(d, state=self._state) for d in data]


class DMChannel(MessageableChannel):
    # Type 1
    ...


class VoiceChannel(MessageableChannel, AudioChannel):
    # Type 2
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        bitrate: int | None | UndefinedType = UNDEFINED,
        user_limit: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | UndefinedType = UNDEFINED,
        parent_id: Snowflake | None | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: VideoQualityMode | None | UndefinedType = UNDEFINED,
    ) -> VoiceChannel:
        return await self._base_edit(
            name=name,
            position=position,
            nsfw=nsfw,
            bitrate=bitrate,
            user_limit=user_limit,
            permission_overwrites=[o.to_dict() for o in permission_overwrites] if permission_overwrites else UNDEFINED,
            parent_id=parent_id,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode.value if video_quality_mode else UNDEFINED,
        )


class GroupDMChannel(MessageableChannel):
    # Type 3
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        icon: str | UndefinedType = UNDEFINED,
    ) -> GroupDMChannel:
        data = await self._state.http.modify_channel(self.id, name=name, icon=icon)
        return GroupDMChannel(data, self._state)


class CategoryChannel(Channel):
    # Type 4
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | UndefinedType = UNDEFINED,
    ) -> CategoryChannel:
        return await self._base_edit(
            name=name,
            position=position,
            permission_overwrites=[o.to_dict() for o in permission_overwrites] if permission_overwrites else UNDEFINED,
        )


class AnnouncementChannel(TextChannel):
    # Type 5
    async def follow(self, target_channel: TextChannel) -> FollowedChannel:
        data = await self._state.http.follow_news_channel(self.id, target_channel.id)
        return FollowedChannel(data)

    async def create_thread(
        self,
        name: str,
        auto_archive_duration: int | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Thread:
        return await super().create_thread(
            name=name,
            auto_archive_duration=auto_archive_duration,
            type=ChannelType.ANNOUNCEMENT_THREAD,
            invitable=invitable,
            rate_limit_per_user=rate_limit_per_user,
            reason=reason,
        )


class Thread(MessageableChannel, GuildChannel):
    # Type 11 & 12
    def __init__(self, data: DiscordChannel, state: State) -> None:
        super().__init__(data, state)
        self.default_thread_rate_limit_per_user: int | UndefinedType = data.get(
            'default_thread_rate_limit_per_user', UndefinedType
        )
        self.message_count: int | UndefinedType = data.get('message_count', UNDEFINED)
        self.thread_metadata: ThreadMetadata | UndefinedType = (
            ThreadMetadata(data['thread_metadata'])
            if data.get('thread_metadata') is not None
            else UNDEFINED
        )
        self.owner_id: Snowflake | UndefinedType = (
            Snowflake(data['owner_id'])
            if data.get('owner_id') is not None
            else UNDEFINED
        )

    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        archived: bool | UndefinedType = UNDEFINED,
        auto_archive_duration: int | UndefinedType = UNDEFINED,
        locked: bool | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | UndefinedType = UNDEFINED,
        flags: ChannelFlags | UndefinedType = UNDEFINED,
        applied_tags: list[ForumTag] | UndefinedType = UNDEFINED,
    ) -> Thread:
        return await self._base_edit(
            name=name,
            archived=archived,
            auto_archive_duration=auto_archive_duration,
            locked=locked,
            invitable=invitable,
            rate_limit_per_user=rate_limit_per_user,
            flags=flags.value if flags else UNDEFINED,
            applied_tags=[t.id for t in applied_tags] if applied_tags else UNDEFINED,
        )

    async def join(self) -> None:
        await self._state.http.join_thread(self.id)

    async def add_member(self, member: Member) -> None:
        await self._state.http.add_thread_member(self.id, member.id)

    async def leave(self) -> None:
        await self._state.http.leave_thread(self.id)

    async def remove_member(self, member: Member) -> None:
        await self._state.http.remove_thread_member(self.id, member.id)

    async def get_member(self, id: Snowflake, *, with_member: bool = True) -> ThreadMember:
        data = await self._state.http.get_thread_member(self.id, id, with_member=with_member)
        return ThreadMember(data)

    async def list_members(
        self, *,
        with_member: bool = True,
        limit: int = 100,
        after: Snowflake | UndefinedType = UNDEFINED,
    ) -> list[ThreadMember]:
        data = await self._state.http.list_thread_members(
            self.id, with_member=with_member, limit=limit, after=after
        )
        return [ThreadMember(d) for d in data]


class AnnouncementThread(Thread):
    # Type 10
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        archived: bool | UndefinedType = UNDEFINED,
        auto_archive_duration: int | UndefinedType = UNDEFINED,
        locked: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | UndefinedType = UNDEFINED,
    ) -> AnnouncementThread:
        return await self._base_edit(
            name=name,
            archived=archived,
            auto_archive_duration=auto_archive_duration,
            locked=locked,
            rate_limit_per_user=rate_limit_per_user,
        )


class StageChannel(AudioChannel):
    # Type 13
    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        bitrate: int | None | UndefinedType = UNDEFINED,
        user_limit: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | UndefinedType = UNDEFINED,
        parent_id: Snowflake | None | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: VideoQualityMode | None | UndefinedType = UNDEFINED,
    ) -> StageChannel:
        return await self._base_edit(
            name=name,
            position=position,
            nsfw=nsfw,
            bitrate=bitrate,
            user_limit=user_limit,
            permission_overwrites=[o.to_dict() for o in permission_overwrites] if permission_overwrites else UNDEFINED,
            parent_id=parent_id,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode.value if video_quality_mode else UNDEFINED,
        )


class DirectoryChannel(Channel):
    # Type 14
    ...


class ForumChannel(Channel):
    # Type 15
    def __init__(self, data: DiscordChannel, state: State) -> None:
        super().__init__(data, state)
        self.default_sort_order: int | None | UndefinedType = data.get(
            'default_sort_order', UndefinedType
        )
        self.default_reaction_emoji: DefaultReaction | UndefinedType = (
            DefaultReaction(data['default_reaction_emoji'])
            if data.get('default_reaction_emoji') is not None
            else UNDEFINED
        )
        self.available_tags: list[ForumTag] = [
            ForumTag.from_dict(d) for d in data.get('available_tags', [])
        ]

    async def edit(
        self, *,
        name: str | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        topic: str | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[_Overwrite] | UndefinedType = UNDEFINED,
        parent_id: Snowflake | None | UndefinedType = UNDEFINED,
        default_auto_archive_duration: int | None | UndefinedType = UNDEFINED,
        flags: ChannelFlags | UndefinedType = UNDEFINED,
        available_tags: list[ForumTag] | UndefinedType = UNDEFINED,
    ) -> ForumChannel:
        return await self._base_edit(
            name=name,
            position=position,
            topic=topic,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            permission_overwrites=[o.to_dict() for o in permission_overwrites] if permission_overwrites else UNDEFINED,
            parent_id=parent_id,
            default_auto_archive_duration=default_auto_archive_duration,
            flags=flags.value if flags else UNDEFINED,
            available_tags=[t.to_dict() for t in available_tags] if available_tags else UNDEFINED,
        )


CHANNEL_TYPE = (
        TextChannel
        | DMChannel
        | VoiceChannel
        | GroupDMChannel
        | CategoryChannel
        | AnnouncementChannel
        | AnnouncementThread
        | Thread
        | StageChannel
        | DirectoryChannel
        | ForumChannel
        | Channel
)


def identify_channel(data: dict[str, Any], state: State) -> CHANNEL_TYPE:
    type = data['type']

    if type == 0:
        return TextChannel(data, state)
    elif type == 1:
        return DMChannel(data, state)
    elif type == 2:
        return VoiceChannel(data, state)
    elif type == 4:
        return CategoryChannel(data, state)
    elif type == 5:
        return AnnouncementChannel(data, state)
    elif type == 10:
        return AnnouncementThread(data, state)
    elif type in (11, 12):
        return Thread(data, state)
    elif type == 13:
        return StageChannel(data, state)
    elif type == 14:
        return DirectoryChannel(data, state)
    elif type == 15:
        return ForumChannel(data, state)
    else:
        return Channel(data, state)
