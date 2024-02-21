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

from __future__ import annotations

from datetime import datetime

from .asset import Asset
from .flags import ChannelFlags, Permissions
from .enums import ChannelType, ForumLayoutType, OverwriteType, SortOrderType, VideoQualityMode
from .missing import Maybe, MISSING
from .mixins import Identifiable, Messageable
from .object import Object
from .user import User

from typing import cast, TYPE_CHECKING, Self, Union

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
        PermissionOverwriteData,
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
        ThreadChannelData,
    ]

    from .mixins import Snowflake
    from .state import State

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
    """
    The bare minimum for a Discord channel. All other channels inherit from this one.

    Attributes
    -----------
    id: :class:`int`
        The ID of the channel.
    type: :class:`ChannelType`
        The type of the channel.
    flags: :class:`ChannelFlags`
        The flags of the channel.
    """
    __slots__ = (
        "_state",
        "id",
        "type",
        "flags",
    )

    def __init__(self, data: ChannelData, state: State) -> None:
        self._state: State = state
        self._update(data)

    def _update(self, data: ChannelData) -> None:
        self.id = int(cast(str, data["id"]))
        self.type: ChannelType = ChannelType(data["type"])
        self.flags: ChannelFlags = ChannelFlags.from_value(flags) \
            if (flags := cast(int, data.get("flags"))) \
            else ChannelFlags(0)

    async def _edit(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError

    async def delete(self, *, reason: str | None = None) -> None:
        # TODO: implement
        raise NotImplementedError


class GuildChannel(BaseChannel):
    # For guilds
    __slots__ = (
        "name",
        "position",
        "permission_overwrites",
    )

    def __init__(self, data: GuildChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: GuildChannelData) -> None:
        super()._update(data)
        self.name: str = cast(str, data["name"])
        self.position: int = cast(int, data["position"])
        self.permission_overwrites: list[PermissionOverwrite] = [
            PermissionOverwrite.from_data(ow) for ow in overwrites
        ] if (overwrites := data.get("permission_overwrites")) else []


class PermissionOverwrite:
    """
    Represents a permission overwrite for a channel.

    This has the same attributes as a :class:`Permissions` object, with the addition of an ID and type.

    Attributes
    -----------
    id: :class:`int`
        The ID of the overwrite.
    type: :class:`str`
        The type of the overwrite.
    """
    __slots__ = (
        "id",
        "type",
        "_allow",
        "_deny",
    )

    def __init__(self, obj: Snowflake, type: OverwriteType, **permissions: dict[str, bool | None]) -> None:
        self.id: int = obj.id
        self.type: OverwriteType = type
        # internal permission flags
        self._allow: Permissions = Permissions(**{k: v if v else False for k, v in permissions.items()})
        self._deny: Permissions = Permissions(**{k: True if v else False for k, v in permissions.items()})

    def __getattr__(self, item: str) -> bool | None:
        if getattr(self._allow, item):
            return True
        if getattr(self._deny, item):
            return False
        return None

    def __setattr__(self, key: str, value: bool | None) -> None:
        if value is None:
            setattr(self._allow, key, False)
            setattr(self._deny, key, False)
        elif value:
            setattr(self._allow, key, True)
            setattr(self._deny, key, False)
        else:
            setattr(self._allow, key, False)
            setattr(self._deny, key, True)

    @classmethod
    def from_data(cls, data: PermissionOverwriteData) -> PermissionOverwrite:
        allow_perms = int(data["allow"])
        deny_perms = int(data["deny"])

        return cls(
            Object(int(data["id"])),
            OverwriteType(data["type"]),
            **{
                k: True if allow_perms & (1 << i) else False if deny_perms & (1 << i) else None
                for k, i in enumerate(Permissions._bitwise_names)
            },
        )

    def to_data(self) -> PermissionOverwriteData:
        return {
            "id": self.id,
            "type": self.type.value,
            "allow": str(self.allow.as_bit),
            "deny": str(self.deny.as_bit),
        }


class TextEnabledChannel(GuildChannel, Messageable):
    # You can text in this one! (still a guild channel)
    __slots__ = (
        "nsfw",
        "last_message_id",
    )

    def __init__(
        self, data: TextChannelData | NewsChannelData | ThreadChannelData | VoiceChannelData, state: State
    ) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: TextChannelData | NewsChannelData | ThreadChannelData | VoiceChannelData) -> None:
        super()._update(data)
        self.nsfw: bool = cast(bool, data.get("nsfw", False))
        self.last_message_id: int | None = int(lmid) \
            if (lmid := cast(int | None, data.get("last_message_id"))) else None


class ChildChannel(BaseChannel):
    # This one can either have parents or be orphaned (loser)
    __slots__ = (
        "parent_id",
    )

    def __init__(self, data: GuildChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: GuildChannelData) -> None:
        super()._update(data)
        self.parent_id: int | None = int(pid) if (pid := cast(int, data.get("parent_id"))) else None


class _ThreadEnabled(ChildChannel, GuildChannel):
    # little thread support
    __slots__ = (
        "default_auto_archive_duration",
    )

    def __init__(
        self, data: TextChannelData | NewsChannelData | ForumChannelData | MediaChannelData, state: State
    ) -> None:
        ChildChannel.__init__(self, data, state)
        GuildChannel.__init__(self, data, state)
        self._update(data)

    def _update(self, data: TextChannelData | NewsChannelData | ForumChannelData | MediaChannelData) -> None:
        ChildChannel._update(self, data)
        GuildChannel._update(self, data)
        self.default_auto_archive_duration: Maybe[int] = cast(
            Maybe[int], data.get("default_auto_archive_duration", MISSING)
        )

    async def list_public_archived_threads(
        self,
        before: datetime | None = None,
        limit: int | None = None,
    ) -> list[Thread]:
        # TODO: implement
        raise NotImplementedError


class ThreadEnabledChannel(_ThreadEnabled):
    # you can make threads
    async def start_thread_from_message(
        self,
        message: Snowflake,
        **kwargs,
    ) -> Thread:
        # TODO: implement
        raise NotImplementedError

    async def start_thread_without_message(
        self,
        **kwargs,
    ) -> Thread:
        # TODO: implement
        raise NotImplementedError

    async def list_private_archived_threads(
        self,
        before: datetime | None = None,
        limit: int | None = None,
    ) -> list[Thread]:
        # TODO: implement
        raise NotImplementedError

    async def list_joined_private_archived_threads(
        self,
        before: datetime | None = None,
        limit: int | None = None,
    ) -> list[Thread]:
        # TODO: implement
        raise NotImplementedError


class ThreadBasedChannel(_ThreadEnabled):
    # this one is only threads
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

    def __init__(self, data: ForumChannelData | MediaChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: ForumChannelData | MediaChannelData) -> None:
        super()._update(data)
        self.topic: str | None = data["topic"]
        self.nsfw: bool = data["nsfw"]
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.available_tags: list[ForumTag] = [ForumTag(tag) for tag in data["available_tags"]]
        self.default_reaction_emoji: DefaultReaction | None = DefaultReaction(data["default_reaction_emoji"]) if (
            data.get("default_reaction_emoji")) else None
        self.default_thread_rate_limit_per_user: int = data["default_thread_rate_limit_per_user"]
        self.default_sort_order: SortOrderType | None = SortOrderType(data["default_sort_order"]) if (
            data.get("default_sort_order")) else None
        self.default_forum_layout: ForumLayoutType = ForumLayoutType(data["default_forum_layout"])

    async def start_thread(
        self,
        **kwargs,
    ) -> "Thread":
        # TODO: implement
        raise NotImplementedError


class ForumTag:
    """
    A tag for a forum channel.

    Attributes
    -----------
    id: :class:`int`
        The ID of the tag.
    name: :class:`str`
        The name of the tag.
    moderated: :class:`bool`
        Whether the tag is moderated.
    emoji_id: :class:`int`
        The ID of the emoji for the tag.
    emoji_name: :class:`str`
        The name of the emoji for the tag.
    """
    __slots__ = (
        "id",
        "name",
        "moderated",
        "emoji_id",
        "emoji_name",
    )

    def __init__(self, data: ForumTagData) -> None:
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.moderated: bool = data["moderated"]
        self.emoji_id: int | None = int(eid) if (eid := data.get("emoji_id")) else None
        self.emoji_name: str | None = data.get("emoji_name")


class DefaultReaction:
    """
    The default reaction for a thread-based channel.

    Attributes
    -----------
    emoji_id: :class:`int`
        The ID of the emoji.
    emoji_name: :class:`str`
        The name of the emoji.
    """
    __slots__ = (
        "emoji_id",
        "emoji_name",
    )

    def __init__(self, data: DefaultReactionData) -> None:
        self.emoji_id: int | None = int(eid) if (eid := data.get("emoji_id")) else None
        self.emoji_name: str | None = data.get("emoji_name")


class VoiceEnabledChannel(ChildChannel, GuildChannel):
    # you can vocally speak!
    __slots__ = (
        "bitrate",
        "user_limit",
    )

    def __init__(self, data: VoiceChannelData, state: State) -> None:
        ChildChannel.__init__(self, data, state)
        GuildChannel.__init__(self, data, state)
        self._update(data)

    def _update(self, data: VoiceChannelData) -> None:
        ChildChannel._update(self, data)
        GuildChannel._update(self, data)
        self.bitrate: int = data["bitrate"]
        self.user_limit: int = data["user_limit"]
        self.rtc_region: str | None = data["rtc_region"]
        self.video_quality_mode: Maybe[VideoQualityMode] = VideoQualityMode(vqm) if (
            vqm := data.get("video_quality_mode")) else MISSING


# Real channel types, finally
class TextChannel(TextEnabledChannel, ThreadEnabledChannel):
    """
    Represents a guild text channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: List[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: Optional[:class:`int`]
        The ID of the last message sent in the channel.
    parent_id: Optional[:class:`int`]
        The ID of the category this channel belongs to.
    topic: Optional[:class:`str`]
        The channel's topic.
    rate_limit_per_user: :class:`int`
        The rate limit per user in seconds.
    last_pin_timestamp: Optional[:class:`datetime.datetime`]
        The timestamp of the last pinned message.
    default_auto_archive_duration: Optional[:class:`int`]
        The default duration for newly created threads in minutes.

    """
    type: ChannelType.GUILD_TEXT

    __slots__ = (
        "topic",
        "rate_limit_per_user",
        "last_pin_timestamp",
        "default_auto_archive_duration",
    )

    def __init__(self, data: TextChannelData, state: State) -> None:
        TextEnabledChannel.__init__(self, data, state)
        ThreadEnabledChannel.__init__(self, data, state)
        self._update(data)

    def _update(self, data: TextChannelData) -> None:
        TextEnabledChannel._update(self, data)
        ThreadEnabledChannel._update(self, data)
        self.topic: str | None = data["topic"]
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(pints) if (
                (pints := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else pints

    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError


class DMChannel(BaseChannel, Messageable):
    """
    Represents a direct message channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    recipients: List[:class:`User`]
        The recipients of the channel.
    last_message_id: Optional[:class:`int`]
        The ID of the last message sent in the channel.
    last_pin_timestamp: Optional[:class:`datetime.datetime`]
        The timestamp of the last pinned message.
    """
    type: ChannelType.DM

    __slots__ = (
        "recipients",
        "last_message_id",
        "last_pin_timestamp",
    )

    def __init__(self, data: DMChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: DMChannelData) -> None:
        super()._update(data)
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.recipients: list[User] = [User(user, self._state) for user in data["recipients"]]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if (
                (lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError

    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError


class VoiceChannel(VoiceEnabledChannel, TextEnabledChannel):
    """
    Represents a guild voice channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: List[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    bitrate: :class:`int`
        The channel's bitrate.
    user_limit: :class:`int`
        The channel's user limit.
    rtc_region: Optional[:class:`str`]
        The channel's RTC region.
    video_quality_mode: Optional[:class:`VideoQualityMode`]
        The channel's video quality mode.
    parent_id: Optional[:class:`int`]
        The ID of the category this channel belongs to.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: Optional[:class:`int`]
        The ID of the last message sent in the channel.
    """
    type: ChannelType.GUILD_VOICE

    def __init__(self, data: VoiceChannelData, state: State) -> None:
        VoiceEnabledChannel.__init__(self, data, state)
        TextEnabledChannel.__init__(self, data, state)
        self._update(data)

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError

    async def connect(self) -> None:
        # TODO: implement
        raise NotImplementedError


class GroupDMChannel(DMChannel):
    """
    Represents a group direct message channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    icon_hash: Optional[:class:`str`]
        The hash of the channel's icon.
    owner_id: :class:`int`
        The ID of the channel's owner.
    application_id: Optional[:class:`int`]
        The ID of the channel's application.
    """
    type: ChannelType.GROUP_DM

    __slots__ = (
        "name",
        "icon_hash",
        "owner_id",
        "application_id",
    )

    def __init__(self, data: GroupDMChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: GroupDMChannelData) -> None:
        super()._update(data)
        self.name: str = data["name"]
        self.icon_hash: str | None = data["icon"]
        self.owner_id: int = int(data["owner_id"])
        self.application_id: int | None = int(appid) if (appid := data.get("application_id")) else None

    @property
    def icon(self) -> Asset | None:
        """:class:`Asset` | None: Returns the channel's icon asset if it exists."""
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
    """
    Represents a guild category channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: List[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    """
    type: ChannelType.GUILD_CATEGORY

    async def modify(self, **kwargs) -> Self:
        # TODO: implement
        raise NotImplementedError


class NewsChannel(TextEnabledChannel, ThreadEnabledChannel):
    """
    Represents a guild announcement channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: list[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: :class:`int` | None
        The ID of the last message sent in the channel.
    topic: :class:`str` | None
        The channel's topic.
    last_pin_timestamp: :class:`datetime.datetime` | None
        The timestamp of the last pinned message.
    default_auto_archive_duration: :class:`int` | None
        The default duration for newly created threads in minutes.
    """
    type: ChannelType.GUILD_ANNOUNCEMENT

    __slots__ = (
        "topic",
        "last_pin_timestamp",
        "default_auto_archive_duration",
    )

    def __init__(self, data: NewsChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: NewsChannelData) -> None:
        super()._update(data)
        self.topic: str | None = data["topic"]
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if (
                (lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts
        self.default_auto_archive_duration: Maybe[int] = data.get("default_auto_archive_duration", MISSING)

    async def get_pinned_messages(self):
        # TODO: implement
        raise NotImplementedError

    async def follow(self, webhook_channel: Snowflake) -> None:
        # TODO: implement
        raise NotImplementedError


class Thread(ChildChannel, Messageable):
    """
    Represents a guild thread channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    last_message_id: :class:`int` | None
        The ID of the last message sent in the channel.
    rate_limit_per_user: :class:`int`
        The rate limit per user in seconds.
    owner_id: :class:`int`
        The ID of the thread's owner.
    last_pin_timestamp: :class:`datetime.datetime` | None
        The timestamp of the last pinned message.
    message_count: :class:`int`
        The number of messages in the thread.
    member_count: :class:`int`
        The number of members in the thread.
    thread_metadata: :class:`ThreadMetadata`
        The metadata of the thread.
    member: :class:`ThreadMember` | None
        The member object of the current user if they are a member of the thread.
    total_messages_sent: :class:`int`
        The total number of messages sent in the thread.
    applied_tags: list[:class:`Snowflake`]
        The tags applied to the thread.
    parent_id: :class:`int` | None
        The ID of the channel this thread belongs to.
    """
    type: Union[ChannelType.ANNOUNCEMENT_THREAD, ChannelType.PUBLIC_THREAD, ChannelType.PRIVATE_THREAD]

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

    def __init__(self, data: ThreadChannelData, state: State) -> None:
        super().__init__(data, state)
        self._update(data)

    def _update(self, data: ThreadChannelData) -> None:
        super()._update(data)
        self.name: str = data["name"]
        self.last_message_id: int | None = int(lmid) if (lmid := data.get("last_message_id")) else None
        self.rate_limit_per_user: int = data["rate_limit_per_user"]
        self.owner_id: int = int(data["owner_id"])
        self.last_pin_timestamp: Maybe[datetime | None] = datetime.fromisoformat(lpts) if (
                (lpts := data.get("last_pin_timestamp", MISSING)) not in (MISSING, None)) else lpts
        self.message_count: int = data["message_count"]
        self.member_count: int = data["member_count"]
        self.thread_metadata: ThreadMetadata = ThreadMetadata.from_data(data["thread_metadata"])
        self.member: ThreadMember | None = ThreadMember.from_data(data["member"]) if (data.get("member")) else None
        self.total_messages_sent: int = data["total_messages_sent"]
        self.applied_tags: list[Snowflake] = [Object(tag) for tag in data["applied_tags"]]

    @property
    def is_private(self) -> bool:
        return self.type == ChannelType.PRIVATE_THREAD

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
    """
    The metadata of a thread.

    Attributes
    -----------
    archived: :class:`bool`
        Whether the thread is archived.
    auto_archive_duration: :class:`int`
        The duration in minutes to automatically archive the thread after recent activity.
    archive_timestamp: :class:`datetime.datetime`
        The timestamp of when the thread was archived.
    locked: :class:`bool`
        Whether the thread is locked.
    invitable: :class:`bool` | None
        Whether the thread is invitable.
    create_timestamp: :class:`datetime.datetime` | None
        The timestamp of when the thread was created.
    """
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
        self.create_timestamp: Maybe[datetime | None] = datetime.fromisoformat(ct) if (
                (ct := data.get("create_timestamp", MISSING)) not in (MISSING, None)) else ct


class ThreadMember:
    """
    A member of a thread.

    Attributes
    -----------
    id: :class:`int`
        The ID of the thread member.
    user_id: :class:`int`
        The ID of the user.
    join_timestamp: :class:`datetime.datetime`
        The timestamp of when the user joined the thread.
    flags: :class:`int`
        The flags of the thread member.
    member: :class:`Member` | None
        The member object of the user if they are a member of the guild.
    """
    __slots__ = (
        "id",
        "user_id",
        "join_timestamp",
        "flags",
        "member",
    )

    def __init__(self, data: "ThreadMemberData") -> None:
        self.id: Maybe[int] = int(tid) if (tid := data.get("id")) else MISSING
        self.user_id: Maybe[int] = int(uid) if (uid := data.get("user_id")) else MISSING
        self.join_timestamp: datetime = datetime.fromisoformat(data["join_timestamp"])
        self.flags: int = data["flags"]
        self.member: Maybe[Member] = Member.from_data(member) if (member := data.get("member")) else MISSING


class StageChannel(VoiceChannel):
    """
    Represents a guild stage channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: List[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    bitrate: :class:`int`
        The channel's bitrate.
    user_limit: :class:`int`
        The channel's user limit.
    rtc_region: Optional[:class:`str`]
        The channel's RTC region.
    video_quality_mode: Optional[:class:`VideoQualityMode`]
        The channel's video quality mode.
    parent_id: Optional[:class:`int`]
        The ID of the category this channel belongs to.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: Optional[:class:`int`]
        The ID of the last message sent in the channel.
    """
    type: ChannelType.GUILD_STAGE_VOICE


class ForumChannel(ThreadBasedChannel):
    """
    Represents a guild forum channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: list[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    topic: :class:`str` | None
        The channel's topic.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: :class:`int` | None
        The ID of the last message sent in the channel.
    rate_limit_per_user: :class:`int`
        The rate limit per user in seconds.
    available_tags: list[:class:`ForumTag`]
        The available tags for the channel.
    default_reaction_emoji: :class:`DefaultReaction` | None
        The default reaction emoji for the channel.
    default_thread_rate_limit_per_user: :class:`int`
        The default thread rate limit per user in seconds.
    default_sort_order: :class:`SortOrderType` | None
        The default sort order for the channel.
    default_forum_layout: :class:`ForumLayoutType`
        The default forum layout for the channel.
    """
    type: ChannelType.GUILD_FORUM


class MediaChannel(ThreadBasedChannel):
    """
    Represents a guild media channel.

    Attributes
    -----------
    type: :class:`ChannelType`
        The channel's type.
    id: :class:`int`
        The channel's ID.
    name: :class:`str`
        The channel's name.
    position: :class:`int`
        The channel's position.
    permission_overwrites: list[:class:`PermissionOverwrite`]
        The channel's permission overwrites.
    topic: :class:`str` | None
        The channel's topic.
    nsfw: :class:`bool`
        Whether the channel is NSFW.
    last_message_id: :class:`int` | None
        The ID of the last message sent in the channel.
    rate_limit_per_user: :class:`int`
        The rate limit per user in seconds.
    available_tags: list[:class:`ForumTag`]
        The available tags for the channel.
    default_reaction_emoji: :class:`DefaultReaction` | None
        The default reaction emoji for the channel.
    default_thread_rate_limit_per_user: :class:`int`
        The default thread rate limit per user in seconds.
    default_sort_order: :class:`SortOrderType` | None
        The default sort order for the channel.
    default_forum_layout: :class:`ForumLayoutType`
        The default forum layout for the channel.
    """
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
channel_types: dict[ChannelType, type[Channel]] = {
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


def channel_factory(data: ChannelData, state: State) -> Channel:
    return channel_types[ChannelType(data["type"])](data, state)
