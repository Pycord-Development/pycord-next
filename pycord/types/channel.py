from typing import Any, Literal, NotRequired, Required, TypedDict

from discord_typings._resources._channel import PartialAttachmentData


class ForumThreadMessageParams(TypedDict, total=False):
    content: str
    embeds: list[dict[str, Any]]
    allowed_mentions: dict[str, Any]
    components: list[dict[str, Any]]
    sticker_ids: list[int]
    attachments: list[PartialAttachmentData]
    flags: int


class ChannelPositionUpdateData(TypedDict, total=False):
    id: Required[int]
    position: int | None
    lock_permissions: bool | None
    parent_id: int | None
