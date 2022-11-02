# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
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
from typing import TYPE_CHECKING

from .enums import ChannelType, OverwriteType, VideoQualityMode
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
from .user import User
from .utils import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class _Overwrite:
    def __init__(self, overwrite: DiscordOverwrite) -> None:
        self.id: Snowflake = Snowflake(overwrite['id'])
        self.type: OverwriteType = OverwriteType(overwrite['type'])
        self.allow: Permissions = Permissions(overwrite['allow'])
        self.deny: Permissions = Permissions(overwrite['deny'])


class ThreadMetadata:
    def __init__(self, metadata: DiscordThreadMetadata) -> None:
        self.archived: bool = metadata['archived']
        self.auto_archive_duration: int = metadata['auto_archive_duration']
        self.archive_timestamp: datetime = datetime.fromisoformat(metadata['archive_timestamp'])
        self.locked: bool = metadata['locked']
        self.invitable: bool | UndefinedType = metadata.get('invitable', UNDEFINED)
        self.create_timestamp: datetime | UndefinedType = (
            datetime.fromisoformat(metadata.get('create_timestamp'))
            if metadata.get('create_timestamp') != None
            else UNDEFINED
        )


class ThreadMember:
    def __init__(self, member: DiscordThreadMember) -> None:
        self._id: str | None = member.get('id')
        self.id: Snowflake | UndefinedType = Snowflake(self._id) if self._id is not None else UNDEFINED
        self._user_id: str | None = member.get('user_id')
        self.user_id: Snowflake | UndefinedType = Snowflake(self._user_id) if self._user_id is not None else UNDEFINED
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
        self.emoji_id: Snowflake | None = Snowflake(self._emoji_id) if self._emoji_id is not None else None
        self.emoji_name: str | None = data['emoji_name']


class Channel:
    def __init__(self, data: DiscordChannel, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.type: ChannelType = ChannelType(data['type'])
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data.get('guild_id')) if data.get('guild_id') is not None else UNDEFINED
        )
        self.position: int | UndefinedType = data.get('position', UNDEFINED)
        self.overwrites: list[_Overwrite] = [_Overwrite(d) for d in data.get('permission_overwrites', [])]
        self.name: str | UndefinedType = data.get('name', UNDEFINED)
        self.topic: str | None | UndefinedType = data.get('topic', UNDEFINED)
        self.nsfw: bool | UndefinedType = data.get('nsfw', UNDEFINED)
        self.last_message_id: int | None | UndefinedType = (
            Snowflake(data.get('last_message_id')) if data.get('last_message_id', UNDEFINED) is not UNDEFINED else UNDEFINED
        )
        self.bitrate: int | UndefinedType = data.get('bitrate', UNDEFINED)
        self.user_limit: int | UndefinedType = data.get('user_limit', UNDEFINED)
        self.rate_limit_per_user: int | UndefinedType = data.get('rate_limit_per_user', UNDEFINED)
        self.recipients: list[User] = [User(d) for d in data.get('recipients', [])]
        self._icon: str | UndefinedType | None = data.get('icon', UndefinedType)
        self.owner_id: Snowflake | UndefinedType = (
            Snowflake(data.get('owner_id')) if data.get('owner_id') is not None else UNDEFINED
        )
        self.application_id: Snowflake | UndefinedType = (
            Snowflake(data.get('application_id')) if data.get('application_id') is not None else UNDEFINED
        )
        self.parent_id: Snowflake | UndefinedType = (
            Snowflake(data.get('parent_id'))
            if data.get('parent_id', UNDEFINED) is not UNDEFINED and data.get('parent_id') is not None
            else data.get('parent_id')
        )
        self.last_pin_timestamp: None | datetime | UndefinedType = (
            datetime.fromisoformat(data.get('last_pin_timestamp'))
            if data.get('last_pin_timestamp') is not None
            else data.get('last_pin_timestamp', UNDEFINED)
        )
        self.rtc_region: str | UndefinedType = data.get('rtc_region', UNDEFINED)
        self.video_quality_mode: VideoQualityMode | UndefinedType = (
            VideoQualityMode(data.get('video_quality_mode')) if data.get('video_quality_mode') is not None else UNDEFINED
        )
        self.message_count: int | UndefinedType = data.get('message_count', UNDEFINED)
        self.thread_metadata: ThreadMetadata | UndefinedType = (
            ThreadMetadata(data.get('thread_metadata')) if data.get('thread_metadata') is not None else UNDEFINED
        )
        self.default_auto_archive_duration: int | UndefinedType = data.get('default_auto_archive_duration', UNDEFINED)
        self.permissions: Permissions | UndefinedType = (
            Permissions._from_value(data.get('permissions')) if data.get('permissions') is not None else UNDEFINED
        )
        self.flags: ChannelFlags | UndefinedType = (
            ChannelFlags._from_value(data.get('flags')) if data.get('flags') is not None else UNDEFINED
        )
        self.total_message_sent: int | UndefinedType = data.get('total_message_sent', UNDEFINED)
        self.available_tags: list[ForumTag] = [ForumTag(d) for d in data.get('available_tags', [])]
        self.applied_tags: list[Snowflake] = [Snowflake(s) for s in data.get('applied_tags', [])]
        self.default_reaction_emoji: DefaultReaction | UndefinedType = (
            DefaultReaction(data.get('default_reaction_emoji')) if data.get('default_reaction_emoji') != None else UNDEFINED
        )
        self.default_thread_rate_limit_per_user: int | UndefinedType = data.get(
            'default_thread_rate_limit_per_user', UndefinedType
        )
        self.default_sort_order: int | None | UndefinedType = data.get('default_sort_order', UndefinedType)
