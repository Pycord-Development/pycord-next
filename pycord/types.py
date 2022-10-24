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
from discord_typings import IntegrationData, StickerPackData
from typing_extensions import NotRequired
from typing import TypedDict

from discord_typings import TextChannelData, VoiceChannelData, NewsChannelData, CategoryChannelData

class ModifyMFALevelData(TypedDict):
    level: int


class PrunedData(TypedDict):
    pruned: int | None


class ListNitroStickerPacksData(TypedDict):
    sticker_packs: list[StickerPackData]


class ConnectionData(TypedDict):
    id: str
    name: str
    type: str
    revoked: NotRequired[bool]
    integrations: NotRequired[list[IntegrationData]]
    verified: bool
    friend_sync: bool
    show_activity: bool
    visibility: int
    
    
GuildChannelData = TextChannelData | VoiceChannelData | NewsChannelData | CategoryChannelData
