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
from .embed import Embed
from .enums import ChannelType, InteractionType, MessageActivityType, MessageType
from .errors import ComponentException
from .flags import MessageFlags
from .media import Attachment, Emoji, Sticker, StickerItem
from .member import Member
from .role import Role
from .snowflake import Snowflake
from .types import (
    AllowedMentions as DiscordAllowedMentions,
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
    from .channel import (
        AnnouncementChannel,
        AnnouncementThread,
        CategoryChannel,
        DirectoryChannel,
        DMChannel,
        ForumChannel,
        StageChannel,
        TextChannel,
        Thread,
        VoiceChannel,
    )
    from .state import State


class ChannelMention:
    __slots__ = ('id', 'guild_id', 'type', 'name')

    def __init__(self, data: DiscordChannelMention) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.type: ChannelType = ChannelType(data['type'])
        self.name: str = data['name']


class Reaction:
    __slots__ = ('count', 'me', 'emoji')

    def __init__(self, data: DiscordReaction) -> None:
        self.count: int = data['count']
        self.me: bool = data['me']
        self.emoji: Emoji = Emoji(data['emoji'])


class MessageActivity:
    __slots__ = ('type', 'party_id')

    def __init__(self, data: DiscordMessageActivity) -> None:
        self.type: MessageActivityType = MessageActivityType(data['type'])
        self.party_id: UndefinedType | str = data.get('party_id', UNDEFINED)


class MessageReference:
    __slots__ = ('message_id', 'channel_id', 'guild_id', 'fail_if_not_exists')

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

    # refactor so user can initialize
    def __init__(
        self,
        message_id: Snowflake | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        guild_id: Snowflake | UndefinedType = UNDEFINED,
        fail_if_not_exists: bool | UndefinedType = UNDEFINED,
    ) -> None:
        self.message_id: Snowflake | UndefinedType = message_id
        self.channel_id: Snowflake | UndefinedType = channel_id
        self.guild_id: Snowflake | UndefinedType = guild_id
        self.fail_if_not_exists: bool | UndefinedType = fail_if_not_exists

    def to_dict(self) -> DiscordMessageReference:
        data = {}
        if self.message_id is not UNDEFINED:
            data['message_id'] = self.message_id
        if self.channel_id is not UNDEFINED:
            data['channel_id'] = self.channel_id
        if self.guild_id is not UNDEFINED:
            data['guild_id'] = self.guild_id
        if self.fail_if_not_exists is not UNDEFINED:
            data['fail_if_not_exists'] = self.fail_if_not_exists
        return data

    @classmethod
    def from_dict(cls, data: DiscordMessageReference) -> MessageReference:
        return cls(
            message_id=data.get('message_id', UNDEFINED),
            channel_id=data.get('channel_id', UNDEFINED),
            guild_id=data.get('guild_id', UNDEFINED),
        )


class MessageInteraction:
    __slots__ = ('id', 'type', 'name', 'user', 'member')

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


class AllowedMentions:
    __slots__ = ('everyone', 'roles', 'users', 'replied_user')

    def __init__(
        self,
        *,
        everyone: bool = False,
        roles: bool | list[Role] = False,
        users: bool | list[User] = False,
        replied_user: bool = False,
    ) -> None:
        self.everyone: bool = everyone
        self.roles: bool | list[Role] = roles
        self.users: bool | list[User] = users
        self.replied_user: bool = replied_user

    def to_dict(self) -> DiscordAllowedMentions:
        data = {}
        parse = []
        if self.everyone is True:
            parse.append('everyone')
        if self.roles is True:
            parse.append('roles')
        elif isinstance(self.roles, list):
            data['roles'] = [r.id for r in self.roles]
        if self.users is True:
            parse.append('users')
        elif isinstance(self.users, list):
            data['users'] = [u.id for u in self.users]
        if self.replied_user is True:
            data['replied_user'] = True
        if parse:
            data['parse'] = parse
        return data


class Message:
    __slots__ = (
        '_state',
        'id',
        'channel_id',
        'author',
        'content',
        'timestamp',
        'edited_timestamp',
        'tts',
        'mentions',
        'mention_roles',
        'attachments',
        'embeds',
        'reactions',
        'nonce',
        'pinned',
        'webhook_id',
        'type',
        'activity',
        'application',
        'application_id',
        'reference',
        'flags',
        'referenced_message',
        'interaction',
        'thread',
        'sticker_items',
        'stickers',
        'position',
        'channel',
    )

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
            MessageReference.from_dict(data.get('message_reference'))
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
            self.channel: TextChannel | DMChannel | VoiceChannel | CategoryChannel | AnnouncementChannel | AnnouncementThread | Thread | StageChannel | DirectoryChannel | ForumChannel = exists[
                1
            ]
        else:
            self.channel: TextChannel | DMChannel | VoiceChannel | CategoryChannel | AnnouncementChannel | AnnouncementThread | Thread | StageChannel | DirectoryChannel | ForumChannel | None = (
                None
            )

    def _modify_from_cache(self, **keys) -> None:
        # this is a bit finnicky but works well
        for k, v in keys.items():
            if hasattr(self, k):
                setattr(self, k, v)

                match k:
                    case 'edited_timestamp':
                        # edited timestamp can't be none on edited messages, I think?
                        self.edited_timestamp = datetime.fromisoformat(v)
                    case 'mentions':
                        self.mentions: list[User] = [User(d, self._state) for d in v]
                    case 'mention_roles':
                        self.mention_roles: list[Snowflake] = [Snowflake(i) for i in v]
                    case 'mention_channels':
                        self.mention_channels: list[ChannelMention] = [
                            ChannelMention(d) for d in v
                        ]
                    case 'attachments':
                        self.attachments: list[Attachment] = [
                            Attachment(a, self._state) for a in v
                        ]
                    case 'embeds':
                        self.embeds: list[Embed] = [Embed._from_data(e) for e in v]
                    case 'reactions':
                        self.reactions: list[Reaction] = [Reaction(r) for r in v]
                    case 'flags':
                        self.flags: MessageFlags = MessageFlags.from_value(v)

    async def crosspost(self) -> Message:
        data = await self._state.http.crosspost_message(self.channel_id, self.id)
        return Message(data, self._state)

    async def add_reaction(self, emoji: Emoji | str) -> None:
        if isinstance(emoji, Emoji):
            emoji = {'id': emoji.id, 'name': emoji.name}
        await self._state.http.create_reaction(
            self.channel_id,
            self.id,
            emoji,
        )

    async def remove_reaction(self, emoji: Emoji | str) -> None:
        if isinstance(emoji, Emoji):
            emoji = {'id': emoji.id, 'name': emoji.name}
        await self._state.http.delete_own_reaction(
            self.channel_id,
            self.id,
            emoji,
        )

    async def remove_user_reaction(self, emoji: Emoji | str, user: User) -> None:
        if isinstance(emoji, Emoji):
            emoji = {'id': emoji.id, 'name': emoji.name}
        await self._state.http.delete_user_reaction(
            self.channel_id,
            self.id,
            emoji,
            user.id,
        )

    async def get_reactions(
        self,
        emoji: Emoji | str,
        *,
        after: Snowflake | UndefinedType = UNDEFINED,
        limit: int = 25,
    ) -> list[User]:
        if isinstance(emoji, Emoji):
            emoji = {'id': emoji.id, 'name': emoji.name}
        data = await self._state.http.get_reactions(
            self.channel_id,
            self.id,
            emoji,
            after=after,
            limit=limit,
        )
        return [User(d, self._state) for d in data]

    async def remove_all_reactions(self, *, emoji: Emoji | str | None = None) -> None:
        if emoji is not None:
            if isinstance(emoji, Emoji):
                emoji = {'id': emoji.id, 'name': emoji.name}
            await self._state.http.delete_all_reactions_for_emoji(
                self.channel_id,
                self.id,
                emoji,
            )
            return
        await self._state.http.delete_all_reactions(
            self.channel_id,
            self.id,
        )

    async def edit(
        self,
        *,
        content: str | None | UndefinedType = UNDEFINED,
        embeds: list[Embed] | None | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentions | None | UndefinedType = UNDEFINED,
        attachments: list[Attachment] | None | UndefinedType = UNDEFINED,
        flags: MessageFlags | None | UndefinedType = UNDEFINED,
    ) -> Message:
        data = await self._state.http.edit_message(
            self.channel_id,
            self.id,
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            attachments=attachments,
            flags=flags,
        )
        return Message(data, self._state)

    async def delete(self, *, reason: str | None = None) -> None:
        await self._state.http.delete_message(self.channel_id, self.id, reason=reason)

    async def reply(self, *args, **kwargs) -> Message:
        kwargs['message_reference'] = MessageReference(
            message_id=self.id,
            channel_id=self.channel_id,
        )
        return await self.channel.send(*args, **kwargs)

    async def pin(self) -> None:
        await self._state.http.pin_message(self.channel_id, self.id)

    async def unpin(self) -> None:
        await self._state.http.unpin_message(self.channel_id, self.id)

    async def create_thread(
        self,
        *,
        name: str,
        auto_archive_duration: int | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | UndefinedType = UNDEFINED,
    ) -> Thread | AnnouncementThread:
        return await self.channel.create_thread(
            self,
            name=name,
            auto_archive_duration=auto_archive_duration,
            rate_limit_per_user=rate_limit_per_user,
        )
