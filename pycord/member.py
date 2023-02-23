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
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .flags import MemberFlags, Permissions
from .role import Role
from .snowflake import Snowflake

if TYPE_CHECKING:
    from .state import State

from .pages import Page
from .pages.paginator import Paginator
from .types import GuildMember
from .undefined import UNDEFINED, UndefinedType
from .user import User


class Member:
    def __init__(
        self, data: GuildMember, state: State, *, guild_id: Snowflake | None = None
    ) -> None:
        self._state: State = state
        self._guild_id: Snowflake | None = guild_id or None
        self.user: User | UndefinedType = (
            User(data.get('user'), state) if data.get('user') is not None else UNDEFINED
        )
        self.nick: str | None | UndefinedType = data.get('nick', UNDEFINED)
        self._avatar: str | None | UndefinedType = data.get('avatar', UNDEFINED)
        self.roles: list[Snowflake] = [Snowflake(s) for s in data['roles']]
        self.joined_at: datetime = datetime.fromisoformat(data['joined_at'])
        self.premium_since: None | UndefinedType | datetime = (
            datetime.fromisoformat(data.get('premium_since'))
            if data.get('premium_since', UNDEFINED) not in [UNDEFINED, None]
            else data.get('premium_since', UNDEFINED)
        )
        self.deaf: bool | UndefinedType = data.get('deaf', UNDEFINED)
        self.mute: bool | UndefinedType = data.get('mute', UNDEFINED)
        self.pending: UndefinedType | bool = data.get('pending', UNDEFINED)
        self.permissions: Permissions | UndefinedType = (
            Permissions.from_value(data.get('permissions'))
            if data.get('permissions', UNDEFINED) is not UNDEFINED
            else UNDEFINED
        )
        self.communication_disabled_until: None | UndefinedType | datetime = (
            datetime.fromisoformat(data.get('communication_disabled_until'))
            if data.get('communication_disabled_until', UNDEFINED)
            not in [UNDEFINED, None]
            else data.get('communication_disabled_until', UNDEFINED)
        )

    async def edit(
        self,
        *,
        nick: str | None | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | UndefinedType = UNDEFINED,
        mute: bool | UndefinedType = UNDEFINED,
        deaf: bool | UndefinedType = UNDEFINED,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        communication_disabled_until: datetime | None | UndefinedType = UNDEFINED,
        flags: MemberFlags | None | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> Member:
        communication_disabled_until = (
            communication_disabled_until.isoformat()
            if communication_disabled_until
            else communication_disabled_until
        )
        data = await self._state.http.modify_guild_member(
            self._guild_id,
            self.user.id,
            nick=nick,
            roles=(roles or []) if roles is not UNDEFINED else roles,
            mute=mute,
            deaf=deaf,
            channel_id=channel_id,
            communication_disabled_until=communication_disabled_until,
            flags=flags.value if flags else flags,
            reason=reason,
        )
        return Member(data, self._state, guild_id=self._guild_id)

    async def add_role(
        self,
        role: Role,
        *,
        reason: str | None = None,
    ) -> None:
        """Adds a role to the member.

        Parameters
        ----------
        role: :class:`Role`
            The role to add.
        reason: :class:`str` | None
            The reason for adding the role. Shows up in the audit log.
        """
        await self._state.http.add_guild_member_role(
            self._guild_id,
            self.id,
            role.id,
            reason=reason,
        )

    async def remove_role(
        self,
        role: Role,
        *,
        reason: str | None = None,
    ) -> None:
        """Removes a role from the member.

        Parameters
        ----------
        role: :class:`Role`
            The role to remove.
        reason: :class:`str` | None
            The reason for removing the role. Shows up in the audit log.
        """
        await self._state.http.remove_guild_member_role(
            self._guild_id,
            self.id,
            role.id,
            reason=reason,
        )

    async def kick(self, *, reason: str | None = None):
        """Kicks the member from the guild.

        Parameters
        ----------
        reason: :class:`str` | None
            The reason for kicking the member. Shows up in the audit log.
        """
        await self._state.http.remove_guild_member(
            self._guild_id,
            self.id,
            reason=reason,
        )


class MemberPage(Page[Member]):
    def __init__(self, member: Member) -> None:
        self.value = member


class MemberPaginator(Paginator[MemberPage]):
    def __init__(
        self,
        state: State,
        guild_id: Snowflake,
        *,
        limit: int = 1,
        after: datetime | None = None,
    ) -> None:
        super().__init__()
        self._state: State = state
        self.guild_id: Snowflake = guild_id
        self.limit: int | None = limit
        if after:
            self.last_id: Snowflake = Snowflake.from_datetime(after)
        else:
            self.last_id: UndefinedType = UNDEFINED
        self.done = False

    async def fill(self):
        if self._previous_page is None or self._previous_page[0] >= len(self._pages):
            if self.done:
                raise StopAsyncIteration
            limit = min(self.limit, 1000) if self.limit else 1000
            if self.limit is not None:
                self.limit -= limit
            data = await self._state.http.list_guild_members(
                self.guild_id,
                limit=limit,
                after=self.last_id,
            )
            if len(data) < limit or self.limit <= 0:
                self.done = True
            if not data:
                raise StopAsyncIteration
            for member in data:
                self.add_page(
                    MemberPage(Member(member, self._state, guild_id=self.guild_id))
                )

    async def forward(self):
        await self.fill()
        value = await super().forward()
        self.last_id = value.user.id
        return value
