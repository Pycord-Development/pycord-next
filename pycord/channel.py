# Copyright (c) 2021-2022 VincentRPS
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
# SOFTWARE.

from datetime import datetime
from typing import cast, Union

from discord_typings import (
    CategoryChannelData,
    ChannelData,
    DMChannelData,
    NewsChannelData,
    PermissionOverwriteData,
    TextChannelData,
    VoiceChannelData,
)
from pycord.abc import Messageable
from pycord.enums import ChannelType
from pycord.mixins import Hashable
from pycord.state import ConnectionState
from pycord.user import User
from pycord.utils import get_and_convert


class GuildChannel(Hashable):
    def __init__(
        self, data: TextChannelData | VoiceChannelData | NewsChannelData | CategoryChannelData, state: ConnectionState
    ) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.type = ChannelType(data['type'])
        self.guild_id = get_and_convert('guild_id', int, data)  # TODO: Grab guild directly
        self.position = data['position']
        self.permission_overwrites: list[PermissionOverwriteData] = [
            cast(PermissionOverwriteData, po) for po in data['permission_overwrites']
        ]
        self.name = data['name']
        self.nsfw = data['nsfw']  # TODO: Remove? Might not be in every guild channel
        self.parent_id = get_and_convert('parent_id', int, data)

    async def _get_channel_id(self):
        return self.id

    async def edit(
        self,
        *,
        reason: str | None = None,
        name: str = ...,
        permission_overwrites: list[PermissionOverwriteData] | None = ...,
        **kwargs,  # these kwargs are not for the user but the internal API
    ):
        if type(self) is GuildChannel and kwargs:
            raise ValueError('The user cannot pass in kwargs, only the internal API can!')

        data = await self._state._app.http.modify_channel(
            self.id,
            reason=reason,
            name=name,
            permission_overwrites=permission_overwrites,
            **kwargs
        )
        # TODO: Replace this channel object in the state with the new one
        return self.__class__(data, self._state)

    async def move(
        self,
        *,
        position: int | None = ...,
        lock_permissions: bool = ...,
        parent: Union['GuildChannel', None] = ...,
    ):
        parent_id = ...
        if parent is not ... and parent is not None:
            parent_id = parent.id
        elif parent is None:
            parent_id = None

        data = await self._state._app.http.modify_channel(
            self.id,
            position=position,
            parent_id=parent_id,  # type: ignore
        )
        # TODO: Sync permissions from the new parent, if set
        return self.__class__(data, self._state)


class DMChannel(Hashable, Messageable):
    def __init__(self, data: DMChannelData, state: ConnectionState) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.type = ChannelType(data['type'])
        self.last_message_id = get_and_convert('last_message_id', int, data)
        self.recipients = [User(d, self._state) for d in data['recipients']]
        self.last_pin_timestamp = get_and_convert('last_pin_timestamp', datetime.fromisoformat, data)

    async def _get_channel_id(self):
        return self.id

class TextChannel(GuildChannel, Messageable):
    def __init__(self, data: TextChannelData | NewsChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)

        self.topic = data.get('topic')
        self.last_message_id = get_and_convert('last_message_id', int, data)
        self.rate_limit_per_user = data.get('rate_limit_per_user')
        self.last_pin_timestamp = get_and_convert('last_pin_timestamp', datetime.fromisoformat, data)

    async def edit(
        self,
        *,
        reason: str | None = None,
        name: str = ...,
        permission_overwrites: list[PermissionOverwriteData] | None = ...,
        type: ChannelType = ...,
        topic: str | None = ...,
        nsfw: bool | None = ...,
        rate_limit_per_user: int | None = ...,
        default_auto_archive_duration: int | None = ...,
    ):
        if type is ...:
            pass
        elif self.type is ChannelType.GUILD_TEXT and type is not ChannelType.GUILD_NEWS:
            raise TypeError('You can only convert Text Channels to News Channels!')
        elif self.type is ChannelType.GUILD_NEWS and type is not ChannelType.GUILD_TEXT:
            raise TypeError('You can only convert News Channels to Text Channels!')

        if rate_limit_per_user is not ... and self.type is not ChannelType.GUILD_TEXT:
            raise ValueError('rate_limit_per_user can only be edited for Text Channels!')

        return await super().edit(
            reason=reason,
            name=name,
            permission_overwrites=permission_overwrites,
            type=type,
            topic=topic,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            default_auto_archive_duration=default_auto_archive_duration,
        )


class VoiceChannel(GuildChannel, Messageable):
    def __init__(self, data: VoiceChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)
        self.pins_supported = False

        self.last_message_id = get_and_convert('last_message_id', int, data)
        self.bitrate = data['bitrate']
        self.user_limit = data['user_limit']
        self.rtc_region = data.get('rtc_region')


class CategoryChannel(GuildChannel):
    def __init__(self, data: CategoryChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)


Channel = Union[TextChannel, DMChannel, VoiceChannel, CategoryChannel]


def _create_channel(data: ChannelData, state: ConnectionState) -> Channel:
    cls = GuildChannel
    match data['type']:
        case 0 | 5:
            cls = TextChannel
        case 1 | 3:
            cls = DMChannel
        case 2:
            cls = VoiceChannel
        case 3:
            # TODO: Group DM channel
            cls = DMChannel
        case 4:
            cls = CategoryChannel
        case 10 | 11 | 12:
            # TODO: Thread channel
            pass
        case 13:
            # TODO: Stage channel
            cls = VoiceChannel
    return cls(data, state)
