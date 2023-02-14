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
from .guilds import _GuildAttr  # type: ignore

if TYPE_CHECKING:
    from ..state import State


class ChannelCreate(Event):
    _name = 'CHANNEL_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []  # type: ignore
        await (state.store.sift('channels')).save(deps, channel.id, channel)  # type: ignore
        self.channel = channel


class ChannelUpdate(Event):
    _name = 'CHANNEL_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []  # type: ignore
        self.previous: CHANNEL_TYPE = await (state.store.sift('channels')).save(  # type: ignore
            deps, channel.id, channel  # type: ignore
        )
        self.channel = channel


class ChannelDelete(Event):
    _name = 'CHANNEL_DELETE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        channel = identify_channel(data, state)

        deps = [channel.guild_id] if hasattr(channel, 'guild_id') else []  # type: ignore
        res = await (state.store.sift('channels')).discard(deps, channel.id)  # type: ignore

        self.cached = res
        self.channel = channel


class ChannelPinsUpdate(_GuildAttr):
    _name = 'CHANNEL_PINS_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.channel_id: Snowflake = Snowflake(data.get('channel_id'))  # type: ignore
        self.guild_id: Snowflake = Snowflake(data.get('guild_id'))  # type: ignore


PinsUpdate = ChannelPinsUpdate


class MessageCreate(Event):
    _name = 'MESSAGE_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        message = Message(data, state)  # type: ignore

        await (state.store.sift('messages')).save(
            [message.channel_id], message.id, message
        )


class MessageUpdate(Event):
    _name = 'MESSAGE_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        message = Message(data, state)  # type: ignore

        self.previous: Message = await (state.store.sift('messages')).save(  # type: ignore
            [message.channel_id], message.id, message
        )
        self.message = message


class MessageDelete(Event):
    _name = 'MESSAGE_DELETE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.message_id = Snowflake('id')
        self.channel_id = Snowflake('channel_id')

        self.message: Message = await (state.store.sift('messages')).discard(  # type: ignore
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
