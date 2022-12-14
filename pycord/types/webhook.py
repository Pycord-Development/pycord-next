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

from .channel import Channel
from .guild import Guild
from .snowflake import Snowflake
from .user import User

WTYPE = Literal[1, 2, 3]


class Webhook(TypedDict):
    id: Snowflake
    type: WTYPE
    guild_id: NotRequired[Snowflake | None]
    channel_id: NotRequired[Snowflake | None]
    user: NotRequired[User]
    name: str | None
    avatar: str | None
    token: NotRequired[str]
    application_id: str | None
    source_guild: NotRequired[Guild]
    source_channel: NotRequired[Channel]
    url: NotRequired[str]
