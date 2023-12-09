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

from .asset import Asset
from .flags import ChannelFlags
from .enums import ChannelType, ForumLayoutType, SortOrderType, VideoQualityMode
from .missing import Maybe, MISSING
from .mixins import Identifiable, Messageable
from .user import User

from typing import TYPE_CHECKING, Self, Union

if TYPE_CHECKING:
    from discord_typings import (
        ChannelData,
        TextChannelData,
        DMChannelData,
        VoiceChannelData,
        GroupDMChannelData,
        CategoryChannelData,
        NewsChannelData,
        ThreadChannelData,
        ForumChannelData,
        MediaChannelData,
        DefaultReactionData, 
        ForumTagData, 
        ThreadMemberData, 
        ThreadMetadataData,
    )

    GuildChannelData = Union[
        TextChannelData, 
        VoiceChannelData,
        CategoryChannelData, 
        NewsChannelData, 
        ForumChannelData, 
        MediaChannelData,
    ]

    from .state import State
    from .utils import Snowflake

__all__ = (
    "Channel",
    "TextChannel",
    "DMChannel",
    "VoiceChannel",
    "GroupDMChannel",
    "CategoryChannel",
    "NewsChannel",
    "Thread",
    "StageChannel",
    "ForumChannel",
    "MediaChannel",
    "channel_factory",
)


class BaseChannel(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "type",
        "flags",
    )

    def __init__(self, data: "ChannelData", state: "State") -> None:
        self._state: "State" = state
        self._update(data)

    def _update(self, data: "ChannelData") -> None:
        self.id = int(data["id"])
        self.type: ChannelType = ChannelType(data["type"])
        self.flags: ChannelFlags = ChannelFlags.from_value(flags) if (flags := data.get("flags")) else ChannelFlags(0)

    async def _edit(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    
    async def delete(self, *, reason: str | None = None) -> None:
        # TODO: implement
        raise NotImplementedError


class GuildChannel(BaseChannel):
    __slots__ = (
        "name",
        "position",
        "permission_overwrites",
    )
    def __init__(self, data: "GuildChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "GuildChannelData") -> None:
        super()._update(data)
        self.name: str = data["name"]
        self.position: int = data["position"]
        self.permission_overwrites: list[PermissionOverwrite] = [PermissionOverwrite.from_data(ow) for ow in overwrites] if (overwrites := data.get("permission_overwrites")) else []


class TextEnabledChannel(GuildChannel, Messageable):
    __slots__ = (
        "nsfw",
        "last_message_id",
    )

    def __init__(self, data: "TextChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "TextChannelData") -> None:
        super()._update(data)
        self.nsfw: bool = data.get("nsfw", False)
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None


class ChildChannel:
    __slots__ = (
        "parent_id",
    )

    def __init__(self, data: "GuildChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "GuildChannelData") -> None:
        super()._update(data)
        self.parent_id: int | None = int(pid) if (pid := data.get("parent_id")) else None


class _ThreadEnabled(ChildChannel, GuildChannel):
    __slots__ = (
        "default_auto_archive_duration",
    )

    def __init__(self, data: "TextChannelData | NewsChannelData | ForumChannelData | MediaChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "TextChannelData | NewsChannelData | ForumChannelData | MediaChannelData") -> None:
        super()._update(data)
        self.default_auto_archive_duration: Maybe[int] = data.get("default_auto_archive_duration", MISSING)
        
    async def list_public_archived_threads(
            self, 
            before: datetime | None = None,
            limit: int | None = None,
    ) -> list[Thread]:
        # TODO: implement
        raise NotImplementedError
        

class ThreadEnabledChannel(_ThreadEnabled):
    async def start_thread_from_message(
            self, 
            message: Snowflake, 
            **kwargs,
    ) -> "Thread":
        # TODO: implement
        raise NotImplementedError
    
    async def start_thread_without_message(
            self, 
            **kwargs,
    ) -> "Thread":
        # TODO: implement
        raise NotImplementedError
    
    async def list_private_archived_threads(
            self, 
            before: datetime | None = None,
            limit: int | None = None,
    ) -> list["Thread"]:
        # TODO: implement
        raise NotImplementedError
    
    async def list_joined_private_archived_threads(
            self, 
            before: datetime | None = None,
            limit: int | None = None,
    ) -> list["Thread"]:
        # TODO: implement
        raise NotImplementedError


class ThreadBasedChannel(_ThreadEnabled):
    __slots__ = (
        "topic",
        "nsfw",
        "last_message_id",
        "rate_limit_per_user",
        "available_tags",
        "default_reaction_emoji",
        "default_thread_rate_limit_per_user",
        "available_tags",
        "default_sort_order",
        "default_forum_layout",
    )

    def __init__(self, data: "ForumChannelData | MediaChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "ForumChannelData | MediaChannelData") -> None:
        super()._update(data)
        self.topic: str | None = data["topic"]
        self.nsfw: bool = data["nsfw"]
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.available_tags: list[ForumTag] = [ForumTag(tag) for tag in data["available_tags"]]
        self.default_reaction_emoji: DefaultReaction | None = DefaultReaction(data["default_reaction_emoji"]) if (data.get("default_reaction_emoji")) else None
        self.default_thread_rate_limit_per_user: int = data["default_thread_rate_limit_per_user"]
        self.default_sort_order: SortOrderType | None = SortOrderType(data["default_sort_order"]) if (data.get("default_sort_order")) else None
        self.default_forum_layout: ForumLayoutType = ForumLayoutType(data["default_forum_layout"])

    async def start_thread(
            self, 
            **kwargs,
    ) -> "Thread":
        # TODO: implement
        raise NotImplementedError
    

class ForumTag:
    __slots__ = (
        "id",
        "name",
        "moderated",
        "emoji_id",
        "emoji_name",
    )

    def __init__(self, data: "ForumTagData") -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.moderated: bool = data["moderated"]
        self.emoji_id: int | None = int(eid) if (eid := data.get("emoji_id")) else None
        self.emoji_name: str | None = data.get("emoji_name")


class DefaultReaction:
    __slots__ = (
        "emoji_id",
        "emoji_name",
    )

    def __init__(self, data: "DefaultReactionData") -> None:
        self.emoji_id: int | None = int(eid) if (eid := data.get("emoji_id")) else None
        self.emoji_name: str | None = data.get("emoji_name")


class VoiceEnabledChannel(ChildChannel, GuildChannel):
    __slots__ = (
        "bitrate",
        "user_limit",
    )

    def __init__(self, data: "VoiceChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "VoiceChannelData") -> None:
        super()._update(data)
        self.bitrate: int = data["bitrate"]
        self.user_limit: int = data["user_limit"]
        self.rtc_region: str | None = data["rtc_region"]
        self.video_quality_mode: Maybe[VideoQualityMode] = VideoQualityMode(vqm) if (vqm := data.get("video_quality_mode")) else MISSING


class TextChannel(TextEnabledChannel, ThreadEnabledChannel):
    type: ChannelType.GUILD_TEXT

    __slots__ = (
        "topic",
        "rate_limit_per_user",
        "last_pin_timestamp",
        "default_auto_archive_duration",
    )

    def __init__(self, data: "TextChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "TextChannelData") -> None:
        super()._update(data)
        self.topic: str | None = data["topic"]
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(pints) if ((pints := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else pints
        self.default_auto_archive_duration: Maybe[int] = data.get("default_auto_archive_duration", MISSING)

    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError
    

class DMChannel(BaseChannel, Messageable):
    type: ChannelType.DM

    __slots__ = (
        "recipients",
        "last_message_id",
        "last_pin_timestamp",
    )

    def __init__(self, data: "DMChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "DMChannelData") -> None:
        super()._update(data)
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.recipients: list[User] = [User(user, self._state) for user in data["recipients"]]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if ((lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    
    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError
    

class VoiceChannel(VoiceEnabledChannel, TextEnabledChannel):
    type: ChannelType.GUILD_VOICE

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    
    async def connect(self) -> None:
        # TODO: implement
        raise NotImplementedError
    

class GroupDMChannel(DMChannel):
    type: ChannelType.GROUP_DM

    __slots__ = (
        "name",
        "icon_hash",
        "owner_id",
        "application_id",
    )

    def __init__(self, data: "GroupDMChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "GroupDMChannelData") -> None:
        super()._update(data)
        self.name: str = data["name"]
        self.icon_hash: str | None = data["icon"]
        self.owner_id: int = int(data["owner_id"])
        self.application_id: int | None = int(appid) if (appid := data.get("application_id")) else None
        
    @property
    def icon(self) -> Asset | None:
        # TODO: i don't know what route this uses, it's not documented
        return 

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    
    async def add_recipient(self, user: Snowflake, access_token: str, nick: str) -> None: 
        # TODO: implement
        raise NotImplementedError
    
    async def remove_recipient(self, user: Snowflake) -> None:
        # TODO: implement
        raise NotImplementedError
    
    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError
    

class CategoryChannel(GuildChannel):
    type: ChannelType.GUILD_CATEGORY

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    

class NewsChannel(TextEnabledChannel, ThreadEnabledChannel):
    type: ChannelType.GUILD_ANNOUNCEMENT

    __slots__ = (
    )

    def __init__(self, data: "NewsChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "NewsChannelData") -> None:
        super()._update(data)
        self.topic: str | None = data["topic"]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if ((lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts
        self.default_auto_archive_duration: Maybe[int] = data.get("default_auto_archive_duration", MISSING)

    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError

    async def follow(self, webhook_channel: Snowflake) -> None:
        # TODO: implement
        raise NotImplementedError


class Thread(ChildChannel, Messageable):
    type: ChannelType.ANNOUNCEMENT_THREAD | ChannelType.PUBLIC_THREAD | ChannelType.PRIVATE_THREAD

    __slots__ = (
        "name",
        "last_message_id",
        "rate_limit_per_user",
        "owner_id",
        "last_pin_timestamp",
        "message_count",
        "member_count",
        "thread_metadata",
        "member",
        "total_messages_sent",
        "applied_tags",
    )

    def __init__(self, data: "ThreadChannelData", state: "State") -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: "ThreadChannelData") -> None:
        super()._update(data)
        self.name: str = data["name"]
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.owner_id: int = int(data["owner_id"])
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if ((lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts
        self.message_count: int = data["message_count"]
        self.member_count: int = data["member_count"]
        self.thread_metadata: ThreadMetadata = ThreadMetadata.from_data(data["thread_metadata"])
        self.member: ThreadMember | None = ThreadMember.from_data(data["member"]) if (data.get("member")) else None
        self.total_messages_sent: int = data["total_messages_sent"]
        self.applied_tags: list[Snowflake] = [Snowflake(tag) for tag in data["applied_tags"]]

    @property
    def is_private(self) -> bool:
        return self.type == ChannelType.GUILD_PRIVATE_THREAD

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError
    
    async def join(self) -> None:
        # TODO: implement
        raise NotImplementedError
    
    async def add_member(self, user: Snowflake) -> None:
        # TODO: implement
        raise NotImplementedError
    
    async def leave(self) -> None:
        # TODO: implement
        raise NotImplementedError
    
    async def remove_member(self, user: Snowflake) -> None:
        # TODO: implement
        raise NotImplementedError
    
    async def get_member(self, user: Snowflake) -> "ThreadMember":
        # TODO: implement
        raise NotImplementedError
    
    async def list_members(self, limit: int = 50, before: Snowflake = None) -> list["ThreadMember"]:
        # TODO: implement
        raise NotImplementedError
    
    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError
    

class ThreadMetadata:
    __slots__ = (
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
        "create_timestamp",
    )

    def __init__(self, data: "ThreadMetadataData") -> None:
        self.archived: bool = data["archived"]
        self.auto_archive_duration: int = data["auto_archive_duration"]
        self.archive_timestamp: datetime = datetime.fromisoformat(data["archive_timestamp"])
        self.locked: bool = data["locked"]
        self.invitable: Maybe[bool] = data.get("invitable", MISSING)
        self.create_timestamp: Maybe[datetime | None] = datetime.fromisoformat(ct) if ((ct := data.get("create_timestamp", MISSING)) not in (MISSING, None)) else ct


class ThreadMember:
    __slots__ = (
        "id",
        "user_id",
        "join_timestamp",
        "flags",
    )

    def __init__(self, data: "ThreadMemberData") -> None:
        self.id: Maybe[int] = int(tid) if (tid := data.get("id")) else MISSING
        self.user_id: Maybe[int] = int(uid) if (uid := data.get("user_id")) else MISSING
        self.join_timestamp: datetime = datetime.fromisoformat(data["join_timestamp"])
        self.flags: int = data["flags"]
        self.member: Maybe[Member] = Member.from_data(member) if (member := data.get("member")) else MISSING


class StageChannel(VoiceChannel):
    type: ChannelType.GUILD_STAGE_VOICE


class ForumChannel(ThreadBasedChannel):
    type: ChannelType.GUILD_FORUM


class MediaChannel(ThreadBasedChannel):
    type: ChannelType.GUILD_MEDIA


Channel = Union[
    TextChannel,
    DMChannel,
    VoiceChannel,
    GroupDMChannel,
    CategoryChannel,
    NewsChannel,
    Thread,
    StageChannel,
    ForumChannel,
    MediaChannel,
]
channel_types: dict[ChannelType, type[BaseChannel]] = {
    ChannelType.GUILD_TEXT: TextChannel,
    ChannelType.DM: DMChannel,
    ChannelType.GUILD_VOICE: VoiceChannel,
    ChannelType.GROUP_DM: GroupDMChannel,
    ChannelType.GUILD_CATEGORY: CategoryChannel,
    ChannelType.GUILD_ANNOUNCEMENT: NewsChannel,
    ChannelType.ANNOUNCEMENT_THREAD: Thread,
    ChannelType.PUBLIC_THREAD: Thread,
    ChannelType.PRIVATE_THREAD: Thread,
    ChannelType.GUILD_STAGE_VOICE: StageChannel,
    ChannelType.GUILD_FORUM: ForumChannel,
    ChannelType.GUILD_MEDIA: MediaChannel,
}

def channel_factory(data: "ChannelData", state: "State") -> Channel:
    return channel_types[ChannelType(data["type"])].from_data(data, state)
