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
from typing import TYPE_CHECKING, Any

from .embed import Embed
from .enums import ChannelType, OverwriteType, VideoQualityMode
from .errors import ComponentException
from .flags import ChannelFlags, Permissions
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
from .user import User

if TYPE_CHECKING:
    from .state import State
    from .ui.house import House


class _Overwrite:
    def __init__(self, overwrite: DiscordOverwrite) -> None:
        self.id: Snowflake = Snowflake(overwrite['id'])
        self.type: OverwriteType = OverwriteType(overwrite['type'])
        self.allow: Permissions = Permissions.from_value(overwrite['allow'])
        self.deny: Permissions = Permissions.from_value(overwrite['deny'])


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


class ForumTag:
    def __init__(self, tag: DiscordForumTag) -> None:
        self.id: Snowflake = Snowflake(tag['id'])
        self.name: str = tag['name']
        self.moderated: bool = tag['moderated']
        self.emoji_id: Snowflake = tag['emoji_id']
        self.emoji_name: str | None = tag['emoji_name']


class DefaultReaction:
    def __init__(self, data: DiscordDefaultReaction) -> None:
        self._emoji_id: str | None = data.get('emoji_id')
        self.emoji_id: Snowflake | None = (
            Snowflake(self._emoji_id) if self._emoji_id is not None else None
        )
        self.emoji_name: str | None = data['emoji_name']


class Channel:
    def __init__(self, data: DiscordChannel, state: State) -> None:
        self._state = state
        self.id: Snowflake = Snowflake(data['id'])
        self.type: ChannelType = ChannelType(data['type'])
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data['guild_id'])
            if data.get('guild_id') is not None
            else UNDEFINED
        )
        self.position: int | UndefinedType = data.get('position', UNDEFINED)
        self.permission_overwrites: list[_Overwrite] = [
            _Overwrite(d) for d in data.get('permission_overwrites', [])
        ]
        self.name: str | UndefinedType = data.get('name', UNDEFINED)
        self.topic: str | None | UndefinedType = data.get('topic', UNDEFINED)
        self.nsfw: bool | UndefinedType = data.get('nsfw', UNDEFINED)
        self.last_message_id: int | None = (
            Snowflake(data['last_message_id'])
            if data.get('last_message_id') is not None
            else None
        )
        self.bitrate: int | UndefinedType = data.get('bitrate', UNDEFINED)
        self.user_limit: int | UndefinedType = data.get('user_limit', UNDEFINED)
        self.rate_limit_per_user: int | UndefinedType = data.get(
            'rate_limit_per_user', UNDEFINED
        )
        self.recipients: list[User] = [User(d) for d in data.get('recipients', [])]
        self._icon: str | UndefinedType | None = data.get('icon', UndefinedType)
        self.owner_id: Snowflake | UndefinedType = (
            Snowflake(data['owner_id'])
            if data.get('owner_id') is not None
            else UNDEFINED
        )
        self.application_id: Snowflake | UndefinedType = (
            Snowflake(data['application_id'])
            if data.get('application_id') is not None
            else UNDEFINED
        )
        self.parent_id: Snowflake | UndefinedType = (
            Snowflake(data['parent_id'])
            if data.get('parent_id') is not None
            else data.get('parent_id', UNDEFINED)
        )
        self.last_pin_timestamp: None | datetime | UndefinedType = (
            datetime.fromisoformat(data['last_pin_timestamp'])
            if data.get('last_pin_timestamp') is not None
            else data.get('last_pin_timestamp', UNDEFINED)
        )
        self.rtc_region: str | UndefinedType = data.get('rtc_region', UNDEFINED)
        self.video_quality_mode: VideoQualityMode | UndefinedType = (
            VideoQualityMode(data['video_quality_mode'])
            if data.get('video_quality_mode') is not None
            else UNDEFINED
        )
        self.message_count: int | UndefinedType = data.get('message_count', UNDEFINED)
        self.thread_metadata: ThreadMetadata | UndefinedType = (
            ThreadMetadata(data['thread_metadata'])
            if data.get('thread_metadata') is not None
            else UNDEFINED
        )
        self.default_auto_archive_duration: int | UndefinedType = data.get(
            'default_auto_archive_duration', UNDEFINED
        )
        self.permissions: Permissions | UndefinedType = (
            Permissions.from_value(data['permissions'])
            if data.get('permissions') is not None
            else UNDEFINED
        )
        self.flags: ChannelFlags | UndefinedType = (
            ChannelFlags.from_value(data['flags'])
            if data.get('flags') is not None
            else UNDEFINED
        )
        self.available_tags: list[ForumTag] = [
            ForumTag(d) for d in data.get('available_tags', [])
        ]
        self.applied_tags: list[Snowflake] = [
            Snowflake(s) for s in data.get('applied_tags', [])
        ]
        self.default_reaction_emoji: DefaultReaction | UndefinedType = (
            DefaultReaction(data['default_reaction_emoji'])
            if data.get('default_reaction_emoji') is not None
            else UNDEFINED
        )
        self.default_thread_rate_limit_per_user: int | UndefinedType = data.get(
            'default_thread_rate_limit_per_user', UndefinedType
        )
        self.default_sort_order: int | None | UndefinedType = data.get(
            'default_sort_order', UndefinedType
        )


class MessageableChannel(Channel):
    async def send(
        self,
        content: str | UndefinedType = UNDEFINED,
        nonce: int | str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        sticker_ids: list[Snowflake] | UndefinedType = UNDEFINED,
        flags: int | UndefinedType = UNDEFINED,
        house: House | UndefinedType = UNDEFINED,
        houses: list[House] | UndefinedType = UNDEFINED,
    ) -> None:
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

        await self._state.http.create_message(
            channel_id=self.id,
            content=content,
            nonce=nonce,
            tts=tts,
            embeds=embeds,
            sticker_ids=sticker_ids,
            flags=flags,
            components=components,
        )


class AudioChannel(Channel):
    ...


class TextChannel(MessageableChannel):
    ...


class DMChannel(MessageableChannel):
    ...


class VoiceChannel(MessageableChannel, AudioChannel):
    ...


class GroupDMChannel(MessageableChannel):
    ...


class CategoryChannel(Channel):
    ...


class AnnouncementChannel(MessageableChannel):
    ...


class AnnouncementThread(MessageableChannel):
    ...


class Thread(MessageableChannel):
    ...


class StageChannel(AudioChannel, Channel):
    ...


class DirectoryChannel(Channel):
    ...


class ForumChannel(Channel):
    ...


def identify_channel(
    data: dict[str, Any], state: State
) -> TextChannel | DMChannel | VoiceChannel | GroupDMChannel | CategoryChannel | AnnouncementChannel | AnnouncementThread | Thread | StageChannel | DirectoryChannel | ForumChannel:
    type = data['type']

    if type == 0:
        return TextChannel(data, state)
    elif type == 1:
        return DMChannel(data, state)
    elif type == 2:
        return VoiceChannel(data, state)
    elif type == 3:
        return GroupDMChannel(data, state)
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
