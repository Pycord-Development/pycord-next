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

from .asset import Asset
from .enums import MembershipState
from .flags import ApplicationFlags, Permissions
from .guild import Guild
from .mixins import Identifiable
from .missing import Maybe, MISSING
from .user import User

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import (
        ApplicationData, PartialApplicationData, InstallParams as InstallParamsData,
        OAuth2Scopes, TeamData, TeamMemberData,
    )
    from .file import File
    from .state import State

__all__ = (
    "Application",
    "InstallParams",
    "Team",
    "TeamMember",
)


class Application(Identifiable):
    """
    Represents a Discord application.

    Attributes
    -----------
    id: :class:`int`
        The application's ID.
    name: :class:`str` | :class:`MISSING`
        The application's name.
    icon_hash: :class:`str` | None | :class:`MISSING`
        The application's icon hash.
    description: :class:`str` | :class:`MISSING`
        The application's description.
    rpc_origins: list[:class:`str`] | :class:`MISSING`
        The application's RPC origins.
    bot_public: :class:`bool` | :class:`MISSING`
        Whether the bot is public.
    bot_require_code_grant: :class:`bool | :class:`MISSING`
        Whether the bot requires a code grant before being added to the server.
    bot: :class:`User` | :class:`MISSING`
        The bot's user object.
    terms_of_service_url: :class:`str | :class:`MISSING`
        The application's terms of service URL.
    privacy_policy_url: :class:`str` | :class:`MISSING`
        The application's privacy policy URL.
    owner: :class:`User` | :class:`MISSING`
        The application's owner.
    verify_key: :class:`str` | :class:`MISSING`
        The application's verification key.
    team: :class:`Team` | None
        The team the application is part of.
    guild_id: :class:`int` | :class:`MISSING`
        The guild ID the application is part of.
    guild: :class:`Guild` | :class:`MISSING`
        The guild the application is part of.
    primary_sku_id: :class:`int` | :class:`MISSING`
        The ID of the application's primary SKU.
    slug: :class:`str` | :class:`MISSING`
        The application's slug.
    cover_image_hash: :class:`str` | :class:`MISSING`
        The application's cover image hash.
    flags: :class:`ApplicationFlags` | :class:`MISSING`
        The application's flags.
    approximate_guild_count: :class:`int` | :class:`MISSING`
        The approximate guild count for the application.
    redirect_uris: list[:class:`str`] | :class:`MISSING`
        The application's redirect URIs.
    role_connections_verification_url: :class:`str` | :class:`MISSING`
        The application's role connection verification URL.
    tags: list[:class:`str`] | :class:`MISSING`
        The application's tags.
    install_params: :class:`InstallParams` | :class:`MISSING`
        The application's install parameters.
    """
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

    def __init__(self, data: ApplicationData | PartialApplicationData, state: State) -> None:
        self._state: State = state
        self.id: int = int(data["id"])
        self.name: Maybe[str] = data.get("name", MISSING)
        self.icon_hash: Maybe[str | None] = data.get("icon", MISSING)
        self.description: Maybe[str] = data.get("description", MISSING)
        self.rpc_origins: Maybe[list[str]] = data.get("rpc_origins", MISSING)
        self.bot_public: Maybe[bool] = data.get("bot_public", MISSING)
        self.bot_require_code_grant: Maybe[bool] = data.get("bot_require_code_grant", MISSING)
        self.bot: Maybe[User] = User(data["bot"], state) if "bot" in data else MISSING
        self.terms_of_service_url: Maybe[str] = data.get("terms_of_service_url", MISSING)
        self.privacy_policy_url: Maybe[str] = data.get("privacy_policy_url", MISSING)
        self.owner: Maybe[User] = User(data["owner"], state) if "owner" in data else MISSING
        self.verify_key: Maybe[str] = data.get("verify_key", MISSING)
        self.team: Team | None = Team(teamdata, state) if (teamdata := data.get("team")) else None
        self.guild_id: Maybe[int] = data.get("guild_id", MISSING)
        self.guild: Maybe[Guild] = Guild(guild, state) if (guild := data.get("guild")) else MISSING
        self.primary_sku_id: Maybe[int] = data.get("primary_sku_id", MISSING)
        self.slug: Maybe[str] = data.get("slug", MISSING)
        self.cover_image_hash: Maybe[str] = data.get("cover_image", MISSING)
        self.flags: Maybe[ApplicationFlags] = ApplicationFlags.from_value(data["flags"]) if "flags" in data else MISSING
        self.approximate_guild_count: Maybe[int] = data.get("approximate_guild_count", MISSING)
        self.redirect_uris: Maybe[list[str]] = data.get("redirect_uris", MISSING)
        self.role_connections_verification_url: Maybe[str] = data.get("role_connections_verification_url", MISSING)
        self.tags: Maybe[list[str]] = data.get("tags", MISSING)
        self.install_params: Maybe[InstallParams] = InstallParams.from_data(
            data["install_params"]
        ) if "install_params" in data else MISSING
        self.custom_install_url: Maybe[str] = data.get("custom_install_url", MISSING)

    def __repr__(self) -> str:
        return f"<Application id={self.id} name={self.name}>"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def icon(self) -> Asset | None:
        """:class:`Asset` | None: The application's icon, if it has one."""
        return Asset.from_application_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None

    @property
    def cover_image(self) -> Asset | None:
        """:class:`Asset` | None: The application's cover image, if it has one."""
        return Asset.from_application_cover(
            self._state, self.id, self.cover_image_hash
        ) if self.cover_image_hash else None

    # TODO: move to client
    async def edit(
        self,
        custom_install_url: Maybe[str] = MISSING,
        description: Maybe[str] = MISSING,
        role_connections_verification_url: Maybe[str] = MISSING,
        install_params: Maybe[InstallParams] = MISSING,
        flags: Maybe[ApplicationFlags] = MISSING,
        icon: Maybe[File] = MISSING,
        cover_image: Maybe[File] = MISSING,
        interactions_endpoint_url: Maybe[str] = MISSING,
        tags: Maybe[list[str]] = MISSING,
    ) -> Application:
        """
        Edits the application.

        All parameters for this method are optional.

        Parameters
        -----------
        custom_install_url: :class:`str`
            The new custom install URL.
        description: :class:`str`
            The new description.
        role_connections_verification_url: :class:`str`
            The new role connections verification URL.
        install_params: :class:`InstallParams`
            The new install parameters.
        flags: :class:`ApplicationFlags`
            The new flags.
        icon: :class:`File`
            The new icon.
        cover_image: :class:`File`
            The new cover image.
        interactions_endpoint_url: :class:`str`
            The new interactions endpoint URL.
        tags: list[:class:`str`]
            The new tags.

        Returns
        --------
        :class:`Application`
            The edited application.

        Raises
        -------
        :exc:`HTTPException`
            Editing the application failed.
        """
        payload = {
            "custom_install_url": custom_install_url,
            "description": description,
            "role_connections_verification_url": role_connections_verification_url,
            "install_params": install_params,
            "flags": flags.as_bit if flags is not MISSING else MISSING,
            "icon": icon,
            "cover_image": cover_image,
            "interactions_endpoint_url": interactions_endpoint_url,
            "tags": tags,
        }
        data = await self._state.http.edit_current_application(**payload)
        return Application(data, self._state)


class InstallParams:
    """
    Represents the default installation parameters for an application.

    Attributes
    -----------
    scopes: list[:class:`str`]
        The default OAuth2 scopes.
    permissions: :class:`Permissions`
        The default permissions requested.
    """
    __slots__ = (
        "scopes",
        "permissions",
    )

    def __init__(self, *, scopes: list[OAuth2Scopes], permissions: Permissions) -> None:
        self.scopes: list[OAuth2Scopes] = scopes
        self.permissions: Permissions = permissions

    def __repr__(self) -> str:
        return f"<InstallParams scopes={self.scopes} permissions={self.permissions}>"

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_data(cls, data: InstallParamsData) -> InstallParams:
        return cls(
            scopes=data["scopes"],
            permissions=Permissions.from_value(data["permissions"]),
        )


class Team(Identifiable):
    """
    Represents a Discord team.

    Attributes
    -----------
    id: :class:`int`
        The team's ID.
    name: :class:`str`
        The team's name.
    icon_hash: :class:`str` | None | :class:`MISSING`
        The team's icon hash.
    members: list[:class:`TeamMember`]
        The team's members.
    owner_user_id: :class:`int`
        The team's owner's user ID.
    """
    __slots__ = (
        "_state",
        "icon_hash",
        "id",
        "members",
        "name",
        "owner_user_id",
    )

    def __init__(self, data: TeamData, state: State) -> None:
        self._state: State = state
        self.icon_hash: str | None = data["icon"]
        self.id: int = int(data["id"])
        self.members: list[TeamMember] = [TeamMember(member, state) for member in data["members"]]
        self.name: str = data["name"]
        self.owner_user_id: int = int(data["owner_user_id"])

    def __repr__(self) -> str:
        return f"<Team id={self.id} name={self.name}>"

    def __str__(self) -> str:
        return self.name

    @property
    def icon(self) -> Asset | None:
        """Optional[:class:`Asset`]: The team's icon, if it has one."""
        return Asset.from_team_icon(self._state, self.id, self.icon_hash) if self.icon_hash else None


class TeamMember(Identifiable):
    """
    Represents a member of a Discord team.

    Attributes
    -----------
    membership_state: :class:`MembershipState`
        The member's membership state (e.g. invited, accepted).
    team_id: :class:`int`
        The team's ID.
    user: :class:`User`
        The member's user object.
    role: :class:`str`
        The member's role in the team.
    """
    __slots__ = (
        "membership_state",
        "team_id",
        "user",
        "role",
    )

    def __init__(self, data: TeamMemberData, state: State) -> None:
        self.membership_state: MembershipState = MembershipState(data["membership_state"])
        self.team_id: int = int(data["team_id"])
        self.user: User = User(data["user"], state)
        self.role: str = data["role"]

    def __repr__(self) -> str:
        return f"<TeamMember user={self.user} role={self.role}>"

    def __str__(self) -> str:
        return str(self.user)
