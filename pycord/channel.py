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
from typing import cast

from discord_typings import (
    CategoryChannelData,
    DMChannelData,
    NewsChannelData,
    PermissionOverwriteData,
    TextChannelData,
    VoiceChannelData,
)

from pycord.enums import ChannelType
from pycord.mixins import Hashable
from pycord.state import ConnectionState
from pycord.user import User
from pycord.utils import _get_and_convert


class GuildChannel(Hashable):
    def __init__(
        self, data: TextChannelData | VoiceChannelData | NewsChannelData | CategoryChannelData, state: ConnectionState
    ) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.type = ChannelType(data['type'])
        self.guild_id = _get_and_convert('guild_id', int, data)  # TODO: Grab guild directly
        self.position = data['position']
        self.permission_overwrites: list[PermissionOverwriteData] = [
            cast(PermissionOverwriteData, po) for po in data['permission_overwrites']
        ]
        self.name = data['name']
        self.nsfw = data['nsfw']  # TODO: Remove? Might not be in every guild channel
        self.parent_id = _get_and_convert('parent_id', int, data)


class DMChannel(Hashable):
    def __init__(self, data: DMChannelData, state: ConnectionState) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.type = ChannelType(data['type'])
        self.last_message_id = _get_and_convert('last_message_id', int, data)
        self.recipients = [User(d, self._state) for d in data['recipients']]
        self.last_pin_timestamp = _get_and_convert('last_pin_timestamp', datetime.fromisoformat, data)


class TextChannel(GuildChannel):
    def __init__(self, data: TextChannelData | NewsChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)

        self.topic = data.get('topic')
        self.last_message_id = _get_and_convert('last_message_id', int, data)
        self.rate_limit_per_user = data.get('rate_limit_per_user')
        self.last_pin_timestamp = _get_and_convert('last_pin_timestamp', datetime.fromisoformat, data)


class VoiceChannel(GuildChannel):
    def __init__(self, data: VoiceChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)

        self.last_message_id = _get_and_convert('last_message_id', int, data)
        self.bitrate = data['bitrate']
        self.user_limit = data['user_limit']
        self.rtc_region = data.get('rtc_region')


class CategoryChannel(GuildChannel):
    def __init__(self, data: CategoryChannelData, state: ConnectionState) -> None:
        GuildChannel.__init__(self, data, state)
