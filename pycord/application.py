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


from .asset import Asset
from .enums import MembershipState
from .flags import ApplicationFlags, Permissions
from .guild import Guild
from .mixins import Identifiable
from .missing import Maybe, MISSING
from .user import User

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import ApplicationData, PartialApplicationData, InstallParams as InstallParamsData, OAuth2Scopes, TeamData, TeamMemberData
    from .state import State

__all__ = (
    "Application",
    "InstallParams",
    "Team",
    "TeamMember",
)

class Application(Identifiable):
    __slots__ = (
        "_state",
        "id",
        "name",
        "icon_hash",
        "description",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "bot",
        "terms_of_service_url",
        "privacy_policy_url",
        "owner",
        "verify_key",
        "team",
        "guild_id",
        "guild",
        "primary_sku_id",
        "slug",
        "cover_image_hash",
        "flags",
        "approximate_guild_count",
        "redirect_uris",
        "role_connections_verification_url",
        "tags",
        "install_params",
        "custom_install_url",
    )

    def __init__(self, data: "ApplicationData | PartialApplicationData", state: "State") -> None:
        self._state: "State" = state
        self.id: int = int(data["id"])
        self.name: Maybe[str] = data.get("name", MISSING)
        self.icon_hash: Maybe[str | None] = data.get("icon", MISSING)
        self.description: Maybe[str] = data.get("description", MISSING)
        self.rpc_origins: Maybe[list[str]] = data.get("rpc_origins", MISSING)
        self.bot_public: Maybe[bool] = data.get("bot_public", MISSING)
        self.bot_require_code_grant: Maybe[bool] = data.get("bot_require_code_grant", MISSING)
        self.bot: Maybe["User"] = User(data["bot"], state) if "bot" in data else MISSING
        self.terms_of_service_url: Maybe[str] = data.get("terms_of_service_url", MISSING)
        self.privacy_policy_url: Maybe[str] = data.get("privacy_policy_url", MISSING)
        self.owner: Maybe["User"] = User(data["owner"], state) if "owner" in data else MISSING
        self.verify_key: Maybe[str] = data.get("verify_key", MISSING)
        self.team: "Team" | None = Team(teamdata, state) if (teamdata := data.get("team")) else None
        self.guild_id: Maybe[int] = data.get("guild_id", MISSING)
        self.guild: Maybe["Guild"] = Guild(guild, state) if (guild := data.get("guild")) else MISSING
        self.primary_sku_id: Maybe[int] = data.get("primary_sku_id", MISSING)
        self.slug: Maybe[str] = data.get("slug", MISSING)
        self.cover_image_hash: Maybe[str] = data.get("cover_image", MISSING)
        self.flags: Maybe[ApplicationFlags] = ApplicationFlags.from_value(data["flags"]) if "flags" in data else MISSING
        self.approximate_guild_count: Maybe[int] = data.get("approximate_guild_count", MISSING)
        self.redirect_uris: Maybe[list[str]] = data.get("redirect_uris", MISSING)
        self.role_connections_verification_url: Maybe[str] = data.get("role_connections_verification_url", MISSING)
        self.tags: Maybe[list[str]] = data.get("tags", MISSING)
        self.install_params: Maybe[InstallParams] = InstallParams(data["install_params"]) if "install_params" in data else MISSING
        self.custom_install_url: Maybe[str] = data.get("custom_install_url", MISSING)

    def __repr__(self) -> str:
        return f"<Application id={self.id} name={self.name}>"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    @property
    def icon(self) -> Asset | None:
        return Asset.from_application_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None

    @property
    def cover_image(self) -> Asset | None:
        return Asset.from_application_cover(self._state, self.id, self.cover_image_hash) if self.cover_image_hash else None


class InstallParams:
    __slots__ = (
        "scopes",
        "permissions",
    )

    def __init__(self, data: "InstallParamsData") -> None:
        self.scopes: list["OAuth2Scopes"] = data["scopes"]
        self.permissions: Permissions = Permissions.from_value(data["permissions"])

    def __repr__(self) -> str:
        return f"<InstallParams scopes={self.scopes} permissions={self.permissions}>"
    
    def __str__(self) -> str:
        return self.__repr__()
    

class Team(Identifiable):
    __slots__ = (
        "_state",
        "icon_hash",
        "id",
        "members",
        "name",
        "owner_user_id",
    )

    def __init__(self, data: "TeamData", state: State) -> None:
        self._state: "State" = state
        self.icon_hash: str | None = data["icon"]
        self.id: int = int(data["id"])
        self.members: list["TeamMember"] = [TeamMember(member, state) for member in data["members"]]
        self.name: str = data["name"]
        self.owner_user_id: int = int(data["owner_user_id"])

    def __repr__(self) -> str:
        return f"<Team id={self.id} name={self.name}>"
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def icon(self) -> Asset | None:
        return Asset.from_team_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None
    

class TeamMember(Identifiable):
    __slots__ = (
        "membership_state",
        "team_id",
        "user",
        "role",
    )

    def __init__(self, data: "TeamMemberData", state: "State") -> None:
        self.membership_state: MembershipState = MembershipState(data["membership_state"])
        self.team_id: int = int(data["team_id"])
        self.user: "User" = User(data["user"], state)
        self.role: str = data["role"]
        
    def __repr__(self) -> str:
        return f"<TeamMember user={self.user} role={self.role}>"
    
    def __str__(self) -> str:
        return str(self.user)
