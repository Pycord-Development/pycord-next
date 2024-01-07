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



from datetime import datetime
from discord_typings import AttachmentData, ChannelMentionData, MessageData
from pycord.asset import Asset
from pycord.enums import ChannelType
from pycord.flags import AttachmentFlags
from pycord.missing import MISSING, Maybe
from pycord.mixins import Identifiable
from pycord.state import State
from pycord.user import User


class Message(Identifiable):
    def __init__(self, data: "MessageData", state: "State") -> None:
        self._state = state
        self._update(data)

    def _update(self, data: "MessageData") -> None:
        self.id: int = int(data["id"])
        self.channel_id: int = int(data["channel_id"])
        self.author: User = User(data=data["author"], state=self._state)
        self.content: str = data["content"]
        self.timestamp: datetime = datetime.fromisoformat(data["timestamp"])
        self.edited_timestamp: datetime | None = datetime.fromisoformat(edited_ts) if (edited_ts := data.get("edited_timestamp")) else None
        self.tts: bool = data["tts"]
        self.mention_everyone: bool = data["mention_everyone"]
        self.mentions: list[User] = [User(data=mention, state=self._state) for mention in data["mentions"]]
        self.mention_roles: list[int] = [int(mention) for mention in data["mention_roles"]]
        self.mention_channels: list[ChannelMention] = [ChannelMention(data=mention, state=self._state) for mention in data["mention_channels"]]
        self.attachments: list[Attachment] = [Attachment(data=attachment, state=self._state) for attachment in data["attachments"]]
        # TODO: embeds, reactions, nonce, pinned, webhook_id, type, activity, application,
        # application_id, message_reference, flags, referenced_message, interaction, thread, 
        # components, sticker_items, stickers, position, role_subcription_data, resolved

class ChannelMention(Identifiable):
    __slots__ = ("id", "guild_id", "type", "name")

    def __init__(self, data: "ChannelMentionData", state: "State") -> None:
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.type: ChannelType = ChannelType(data["type"])
        self.name: str = data["name"]
    

class Attachment(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "filename",
        "description",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
        "ephemeral",
        "duration_secs",
        "waveform",
        "flags",
    )

    def __init__(self, data: "AttachmentData", state: "State") -> None:
        self._state = state
        self.id: int = int(data["id"])
        self.filename: str = data["filename"]
        self.description: Maybe[str] = data.get("description", MISSING)
        self.size: int = data["size"]
        self.url: str = data["url"]
        self.proxy_url: str = data["proxy_url"]
        self.height: Maybe[int | None] = data.get("height", MISSING)
        self.width: Maybe[int | None] = data.get("width", MISSING)
        self.ephemeral: Maybe[bool] = data.get("ephemeral", MISSING)
        self.duration_secs: Maybe[int] = data.get("duration_secs", MISSING)
        self.waveform: Maybe[str] = data.get("waveform", MISSING)
        self.flags: Maybe[AttachmentFlags] = AttachmentFlags.from_value(flags) if (flags := data.get("flags")) else MISSING

    @property
    def asset(self) -> Asset:
        return Asset(self._state, url=self.url)
    
    @property
    def proxy_asset(self) -> Asset:
        return Asset(self._state, url=self.proxy_url)