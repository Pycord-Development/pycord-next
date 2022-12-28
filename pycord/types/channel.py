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
from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .snowflake import Snowflake
from .user import User

CTYPE = Literal[0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15]


class Overwrite(TypedDict):
    id: Snowflake
    type: int
    allow: str
    deny: str


class ThreadMetadata(TypedDict):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: str
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[str | None]


class ThreadMember(TypedDict):
    id: NotRequired[Snowflake]
    user_id: NotRequired[Snowflake]
    join_timestamp: str
    flags: int


class ForumTag(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: Snowflake
    emoji_name: str | None


class DefaultReaction(TypedDict):
    emoji_id: str | None
    emoji_name: str | None


class Channel(TypedDict):
    id: Snowflake
    type: CTYPE
    guild_id: NotRequired[Snowflake]
    position: NotRequired[Snowflake]
    permission_overwrites: NotRequired[list[Overwrite]]
    name: NotRequired[str | None]
    topic: NotRequired[str | None]
    nsfw: NotRequired[bool]
    last_message_id: NotRequired[Snowflake | None]
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rate_limit_per_user: NotRequired[int]
    recipients: NotRequired[list[User]]
    icon: NotRequired[str | None]
    owner_id: NotRequired[Snowflake]
    application_id: NotRequired[Snowflake]
    parent_id: NotRequired[Snowflake | None]
    last_pin_timestamp: NotRequired[str | None]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[Literal[1, 2]]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: NotRequired[ThreadMetadata]
    member: NotRequired[ThreadMember]
    default_auto_archive_duration: NotRequired[int]
    permissions: NotRequired[int]
    flags: NotRequired[int]
    total_messages_sent: NotRequired[int]
    available_tags: list[ForumTag]
    applied_tags: list[Snowflake]
    default_reaction_emoji: NotRequired[DefaultReaction]
    default_thread_rate_limit_per_user: NotRequired[int]
    default_sort_order: NotRequired[int | None]


AMTYPE = Literal['roles', 'users', 'everyone']


class AllowedMentions(TypedDict):
    parse: list[AMTYPE]
    roles: list[Snowflake]
    users: list[Snowflake]
    replied_user: bool
