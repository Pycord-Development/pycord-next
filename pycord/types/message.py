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

from .application import Application
from .channel import CTYPE, Channel
from .component import Component
from .embed import Embed
from .guild import GuildMember
from .media import Attachment, Emoji, Sticker, StickerItem
from .role import Role
from .snowflake import Snowflake
from .user import User

MTYPE = Literal[
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
]


class ChannelMention(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    type: CTYPE
    name: str


class Reaction(TypedDict):
    count: int
    me: bool
    emoji: Emoji


class MessageActivity(TypedDict):
    type: Literal[1, 2, 3, 5]
    party_id: str


class MessageReference(TypedDict):
    message_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    guild_id: NotRequired[Snowflake]
    fail_if_not_exists: NotRequired[bool]


class MessageInteraction(TypedDict):
    id: Snowflake
    type: Literal[1, 2, 3, 4, 5]
    name: str
    user: User
    member: NotRequired[GuildMember]


class Message(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    author: NotRequired[User]
    content: NotRequired[str]
    timestamp: str
    edited_timestamp: str | None
    tts: bool
    mention_everyone: bool
    mentions: list[User]
    mention_roles: list[Role]
    mention_channels: NotRequired[list[ChannelMention]]
    attachments: list[Attachment]
    embeds: list[Embed]
    reactions: list[Reaction]
    nonce: NotRequired[int | str]
    pinned: bool
    webhook_id: Snowflake
    type: int
    activity: NotRequired[MessageActivity]
    application: NotRequired[Application]
    application_id: NotRequired[Snowflake]
    message_reference: NotRequired[MessageReference]
    flags: NotRequired[int]
    referenced_message: NotRequired['Message']
    interaction: NotRequired[MessageInteraction]
    thread: NotRequired[Channel]
    components: NotRequired[list[Component]]
    sticker_items: NotRequired[list[StickerItem]]
    stickers: NotRequired[list[Sticker]]
    position: NotRequired[int]
