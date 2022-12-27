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

from .enums import MembershipState
from .snowflake import Snowflake
from .types import (
    Team as DiscordTeam,
    TeamMember as DiscordTeamMember,
)
from .user import User


class TeamMember:
    def __init__(self, data: DiscordTeamMember) -> None:
        self.team_id: Snowflake = Snowflake(data['team_id'])
        self.user = User(data['user'])
        self.permissions: list[str] = data['permissions']
        self.membership_state: MembershipState = MembershipState(
            data['membership_state']
        )


class Team:
    def __init__(self, data: DiscordTeam) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.icon: str | None = data['icon']
        self.members: list[TeamMember] = [TeamMember(d) for d in data['members']]
        self.name: str = data['name']
        self.owner_id: Snowflake = Snowflake(data['owner_user_id'])
