from typing import Literal, NotRequired, TypedDict


class RolePositionUpdateData(TypedDict):
    id: int
    position: NotRequired[int | None]


class MFALevelResponse(TypedDict):
    mfa_level: Literal[0, 1]


class PruneCountResponse(TypedDict):
    pruned: int


class VanityURLData(TypedDict):
    code: str | None
    uses: int
