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
from .snowflake import Snowflake
from .types import (
    WelcomeScreen as DiscordWelcomeScreen,
    WelcomeScreenChannel as DiscordWelcomeScreenChannel,
)


class WelcomeScreenChannel:
    def __init__(self, data: DiscordWelcomeScreenChannel) -> None:
        self.channel_id: Snowflake = Snowflake(data['channel_id'])
        self.description: str = data['description']
        self.emoji_id: Snowflake | None = (
            Snowflake(data['emoji_id']) if data['emoji_id'] is not None else None
        )
        self.emoji_name: str | None = data['emoji_name']


class WelcomeScreen:
    def __init__(self, data: DiscordWelcomeScreen) -> None:
        self.description: str | None = data['description']
        self.welcome_channels: list[WelcomeScreenChannel] = []
        self.welcome_channels.extend(
            WelcomeScreenChannel(welcome_channel)
            for welcome_channel in data['welcome_channels']
        )
