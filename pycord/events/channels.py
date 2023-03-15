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

from typing import TYPE_CHECKING, Any

from ..channel import CHANNEL_TYPE, identify_channel
from ..message import Message
from ..snowflake import Snowflake
from .event_manager import Event
from .guilds import _GuildAttr

if TYPE_CHECKING:
    from ..state import State


class ChannelCreate(Event):
    _name = 'CHANNEL_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []
        await (state.store.sift('channels')).save(deps, channel.id, channel)
        self.channel = channel


class ChannelUpdate(Event):
    _name = 'CHANNEL_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []
        self.previous: CHANNEL_TYPE = await (state.store.sift('channels')).save(
            deps, channel.id, channel
        )
        self.channel = channel


class ChannelDelete(Event):
    _name = 'CHANNEL_DELETE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []
        res = await (state.store.sift('channels')).discard(deps, channel.id)

        self.cached = res
        self.channel = channel


class ChannelPinsUpdate(_GuildAttr):
    _name = 'CHANNEL_PINS_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.channel_id: Snowflake = Snowflake(data.get('channel_id'))
        self.guild_id: Snowflake = Snowflake(data.get('guild_id'))


PinsUpdate = ChannelPinsUpdate


class MessageCreate(Event):
    _name = 'MESSAGE_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        message = Message(data, state)
        self.message = message
        self.is_human = message.author.bot is False
        self.content = self.message.content

        await (state.store.sift('messages')).save(
            [message.channel_id], message.id, message
        )


class MessageUpdate(Event):
    _name = 'MESSAGE_UPDATE'

    previous: Message | None
    message: Message

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.previous: Message | None = await (state.store.sift('messages')).get_one(
            [int(data['channel_id'])], int(data['id'])
        )
        if self.previous is None:
            message = Message(data, state)
            await state.store.sift('messages').insert(
                [message.channel_id], message.id, message
            )
        else:
            message: Message = self.previous
            message._modify_from_cache(**data)

        self.message = message


class MessageDelete(Event):
    _name = 'MESSAGE_DELETE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.message_id: Snowflake = Snowflake(data['id'])
        self.channel_id: Snowflake = Snowflake(data['channel_id'])
        self.guild_id: Snowflake | None = (
            Snowflake(data['guild_id']) if 'guild_id' in data else None
        )

        self.message: Message | None = await (state.store.sift('messages')).discard(
            [self.channel_id], self.message_id
        )


class MessageBulkDelete(Event):
    _name = 'MESSAGE_DELETE_BULK'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel_id = Snowflake(data['channel_id'])
        bulk: list[Message | int] = [
            (await (state.store.sift('messages')).discard([channel_id], message_id))
            or message_id
            for message_id in (Snowflake(id) for id in data['ids'])
        ]
        self.deleted_messages = bulk
        self.length = len(bulk)
