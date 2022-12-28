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

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING

from .application import Application
from .channel import (
    AnnouncementChannel,
    AnnouncementThread,
    CategoryChannel,
    DirectoryChannel,
    DMChannel,
    ForumChannel,
    GroupDMChannel,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
)
from .embed import Embed
from .enums import ChannelType, InteractionType, MessageActivityType, MessageType
from .flags import MessageFlags
from .media import Attachment, Emoji, Sticker, StickerItem
from .member import Member
from .snowflake import Snowflake
from .types import (
    ChannelMention as DiscordChannelMention,
    Message as DiscordMessage,
    MessageActivity as DiscordMessageActivity,
    MessageInteraction as DiscordMessageInteraction,
    MessageReference as DiscordMessageReference,
    Reaction as DiscordReaction,
)
from .undefined import UNDEFINED, UndefinedType
from .user import User

if TYPE_CHECKING:
    from .state import State


class ChannelMention:
    def __init__(self, data: DiscordChannelMention) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.type: ChannelType = ChannelType(data['type'])
        self.name: str = data['name']


class Reaction:
    def __init__(self, data: DiscordReaction) -> None:
        self.count: int = data['count']
        self.me: bool = data['me']
        self.emoji: Emoji = Emoji(data['emoji'])


class MessageActivity:
    def __init__(self, data: DiscordMessageActivity) -> None:
        self.type: MessageActivityType = MessageActivityType(data['type'])
        self.party_id: UndefinedType | str = data.get('party_id', UNDEFINED)


class MessageReference:
    def __init__(self, data: DiscordMessageReference) -> None:
        self.message_id: Snowflake | UndefinedType = (
            Snowflake(data.get('message_id'))
            if data.get('message_id') is not None
            else UNDEFINED
        )
        self.channel_id: Snowflake | UndefinedType = (
            Snowflake(data.get('channel_id'))
            if data.get('channel_id') is not None
            else UNDEFINED
        )
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(data.get('guild_id'))
            if data.get('guild_id') is not None
            else UNDEFINED
        )
        self.fail_if_not_exists: bool | UndefinedType = data.get(
            'fail_if_not_exists', UNDEFINED
        )


class MessageInteraction:
    def __init__(self, data: DiscordMessageInteraction, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.type: InteractionType = InteractionType(data['type'])
        self.name: str = data['name']
        self.user: User = User(data['user'], state)
        self.member: Member | UndefinedType = (
            Member(data.get('member'), state)
            if data.get('member') is not None
            else UNDEFINED
        )


class Message:
    def __init__(self, data: DiscordMessage, state: State) -> None:
        self._state = state
        self.id: Snowflake = Snowflake(data['id'])
        self.channel_id: Snowflake = Snowflake(data['channel_id'])
        self.author: User = User(data['author'], state=state)
        self.content: str = data['content']
        self.timestamp: datetime = datetime.fromisoformat(data['timestamp'])
        self.edited_timestamp: datetime | None = (
            datetime.fromisoformat(data['edited_timestamp'])
            if data['edited_timestamp'] is not None
            else None
        )
        self.tts: bool = data['tts']
        self.mentions: list[User] = [User(d, state) for d in data['mentions']]
        self.mention_roles: list[Snowflake] = [
            Snowflake(i) for i in data['mention_roles']
        ]
        self.mention_channels: list[ChannelMention] = [
            ChannelMention(d) for d in data.get('mention_channels', [])
        ]
        self.attachments: list[Attachment] = [
            Attachment(a, state) for a in data['attachments']
        ]
        self.embeds: list[Embed] = [Embed._from_data(e) for e in data['embeds']]
        self.reactions: list[Reaction] = [
            Reaction(r) for r in data.get('reactions', [])
        ]
        self.nonce: UndefinedType | int | str = data.get('nonce', UNDEFINED)
        self.pinned: bool = data['pinned']
        self.webhook_id: Snowflake = (
            Snowflake(data.get('webhook_id'))
            if data.get('webhook_id') is not None
            else UNDEFINED
        )
        self.type: MessageType = MessageType(data['type'])
        self.activity: MessageActivity | UndefinedType = (
            MessageActivity(data.get('activity'))
            if data.get('activity') is not None
            else UNDEFINED
        )
        self.application: Application | UndefinedType = (
            Application(data.get('application'))
            if data.get('application') is not None
            else UNDEFINED
        )
        self.application_id: Snowflake | UndefinedType = (
            Snowflake(data.get('application_id'))
            if data.get('application_id') is not None
            else UNDEFINED
        )
        self.reference: MessageReference | UndefinedType = (
            MessageReference(data.get('message_reference'))
            if data.get('message_reference') is not None
            else UNDEFINED
        )
        self.flags: MessageFlags | UndefinedType = (
            MessageFlags.from_value(data.get('flags'))
            if data.get('flags') is not None
            else UNDEFINED
        )
        self.referenced_message: Message | UndefinedType = (
            Message(data.get('referenced_message'), state)
            if data.get('referenced_message') is not None
            else UNDEFINED
        )
        self.interaction: MessageInteraction | UndefinedType = (
            MessageInteraction(data.get('interaction'), state)
            if data.get('interaction') is not None
            else UNDEFINED
        )
        self.thread: Thread | UndefinedType = (
            Thread(data.get('thread'), state=state)
            if data.get('thread') is not None
            else UNDEFINED
        )
        # TODO: Work on components
        # self.components
        self.sticker_items: list[StickerItem] = [
            StickerItem(si) for si in data.get('sticker_items', [])
        ]
        self.stickers: list[Sticker] = [Sticker(s) for s in data.get('stickers', [])]
        self.position: UndefinedType | int = data.get('position', UndefinedType)
        asyncio.create_task(self._retreive_channel())

    async def _retreive_channel(self) -> None:
        exists = await (self._state.store.sift('channels')).get_without_parents(
            self.channel_id
        )

        if exists:
            self.channel: TextChannel | DMChannel | VoiceChannel | GroupDMChannel | CategoryChannel | AnnouncementChannel | AnnouncementThread | Thread | StageChannel | DirectoryChannel | ForumChannel = exists[
                1
            ]
        else:
            self.channel: TextChannel | DMChannel | VoiceChannel | GroupDMChannel | CategoryChannel | AnnouncementChannel | AnnouncementThread | Thread | StageChannel | DirectoryChannel | ForumChannel = (
                None
            )
