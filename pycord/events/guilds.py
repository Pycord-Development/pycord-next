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


import functools
from typing import TYPE_CHECKING, Any

from ..channel import Channel, Thread, identify_channel
from ..guild import Guild
from ..member import Member
from ..role import Role
from ..scheduled_event import ScheduledEvent
from ..snowflake import Snowflake
from ..stage_instance import StageInstance
from ..user import User
from .event_manager import Event

if TYPE_CHECKING:
    from ..state import State


class _GuildAttr(Event):
    guild_id: int | None

    @functools.cached_property
    async def guild(self) -> Guild | None:
        if self.guild_id is None:
            return None

        guild = await (self._state.store.sift('guilds')).get_one(
            [self.guild_id], self.guild_id
        )

        return guild


class _MemberAttr(Event):
    user_id: int | None
    guild_id: int | None

    @functools.cached_property
    async def member(self) -> Guild | None:
        if self.user_id is None:
            return None

        member = await (self._state.store.sift('members')).get_one(
            [self.guild_id], self.user_id
        )

        return member


class GuildCreate(Event):
    _name = 'GUILD_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        self.guild = Guild(data, state=state)
        self.channels: list[Channel] = [
            identify_channel(c, state) for c in data['channels']
        ]
        self.threads: list[Thread] = [
            identify_channel(c, state) for c in data['threads']
        ]
        self.stage_instances: list[StageInstance] = [
            StageInstance(st, state) for st in data['stage_instances']
        ]
        self.guild_scheduled_events: list[ScheduledEvent] = [
            ScheduledEvent(se, state) for se in data['guild_scheduled_events']
        ]

        await (state.store.sift('guilds')).save(
            [self.guild.id], self.guild.id, self.guild
        )

        for channel in self.channels:
            await (state.store.sift('channels')).save(
                [self.guild.id], channel.id, channel
            )

        for thread in self.threads:
            await (state.store.sift('threads')).save(
                [self.guild.id, thread.parent_id], thread.id, thread
            )

        for stage in self.stage_instances:
            await (state.store.sift('stages')).save(
                [stage.channel_id, self.guild.id, stage.guild_scheduled_event_id],
                stage.id,
                stage,
            )

        for scheduled_event in self.guild_scheduled_events:
            await (state.store.sift('scheduled_events')).save(
                [
                    scheduled_event.channel_id,
                    scheduled_event.creator_id,
                    scheduled_event.entity_id,
                    self.guild.id,
                ],
                scheduled_event.id,
                scheduled_event,
            )


class GuildAvailable(GuildCreate):
    """
    Event denoting the accessibility of a previously joined Guild.
    """

    async def _is_publishable(self, data: dict[str, Any], state: 'State') -> bool:
        return True if int(data['id']) in state._available_guilds else False


class GuildJoin(GuildCreate):
    async def _is_publishable(self, data: dict[str, Any], state: 'State') -> bool:
        exists = True if int(data['id']) in state._available_guilds else False

        if exists:
            return False

        state._available_guilds.append(int(data['id']))
        return True


class GuildUpdate(Event):
    _name = 'GUILD_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild = Guild(data=data, state=state)
        res = await (state.store.sift('guilds')).save([guild.id], guild.id, guild)

        self.previous = res

        self.guild = guild


class GuildDelete(Event):
    _name = 'GUILD_DELETE'

    async def _is_publishable(self, data: dict[str, Any], _state: 'State') -> bool:
        if data.get('unavailable', None) is not None:
            return True
        else:
            return False

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id = Snowflake(data['guild_id'])
        res = await (state.store.sift('guilds')).discard([guild_id], guild_id, Guild)

        self.guild = res
        self.guild_id = guild_id


class GuildBanCreate(_GuildAttr):
    _name = 'GUILD_BAN_ADD'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id: Snowflake = Snowflake(data['guild_id'])

        self.guild_id = guild_id
        self.user = User(data['user'])


GuildBanAdd = GuildBanCreate
BanAdd = GuildBanCreate


class GuildBanDelete(_GuildAttr):
    _name = 'GUILD_BAN_REMOVE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id: Snowflake = Snowflake(data['guild_id'])

        self.guild_id = guild_id
        self.user = User(data['user'])


BanDelete = GuildBanDelete


class GuildMemberAdd(_GuildAttr):
    _name = 'GUILD_MEMBER_ADD'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id = Snowflake(data['guild_id'])
        member = Member(data, state, guild_id=guild_id)
        if state.cache_guild_members:
            await (state.store.sift('members')).insert(
                [guild_id], member.user.id, member
            )

        self.guild_id = guild_id
        self.member: Member = member


MemberJoin = GuildMemberAdd


class GuildMemberUpdate(_GuildAttr):
    _name = 'GUILD_MEMBER_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id = Snowflake(data['guild_id'])
        member = Member(data, state, guild_id=guild_id)

        res = await (state.store.sift('members')).save(
            [guild_id], member.user.id, member
        )

        self.member: Member = res
        self.guild_id = guild_id
        self.previous = res


MemberEdit = GuildMemberUpdate


class GuildMemberRemove(_GuildAttr):
    _name = 'GUILD_MEMBER_REMOVE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.user_id: Snowflake = Snowflake(data['user']['id'])

        self.user = User(data['user'], state)

        await (state.store.sift('members')).discard([self.guild_id], self.user_id)


MemberRemove = GuildMemberRemove


class GuildMemberChunk(Event):
    _name = 'GUILD_MEMBER_CHUNK'

    async def _is_publishable(self, _data: dict[str, Any], _state: 'State') -> bool:
        return False

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        ms: list[Member] = [
            await (state.store.sift('members')).save([guild_id], member.user.id, member)
            for member in (
                Member(member_data, state, guild_id=guild_id) for member_data in data['members']
            )
        ]
        self.members = ms


MemberChunk = GuildMemberChunk


class GuildRoleCreate(_GuildAttr):
    _name = 'GUILD_ROLE_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        role = Role(data['role'], state)

        await (state.store.sift('roles')).insert([self.guild_id], role.id, role)

        self.role = role


RoleCreate = GuildRoleCreate


class GuildRoleUpdate(_GuildAttr):
    _name = 'GUILD_ROLE_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        guild_id: Snowflake = Snowflake(data['guild_id'])
        role = Role(data['role'], self)

        await (state.store.sift('roles')).save([guild_id], role.id, role)

        self.role = role


RoleUpdate = GuildRoleUpdate


class GuildRoleDelete(_GuildAttr):
    _name = 'GUILD_ROLE_DELETE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.role_id: Snowflake = Snowflake(data['role_id'])

        self.role: Role | None = await (state.store.sift('roles')).discard(
            [self.guild_id], self.role_id
        )


RoleDelete = GuildRoleDelete
