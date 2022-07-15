# Copyright (c) 2021-2022 VincentRPS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from discord_typings import GuildMemberData, PartialGuildData, Snowflake, UserData

from pycord.mixins import RouteCategoryMixin
from pycord.internal.http.route import Route
from pycord.types import ConnectionData


class UserRoutes(RouteCategoryMixin):
    async def get_current_user(self) -> UserData:
        return await self.request('GET', Route('/users/@me'), None)

    async def get_user(self, user_id: Snowflake) -> UserData:
        return await self.request('GET', Route('/users/{user_id}', user_id=user_id), None)

    async def modify_current_user(
        self,
        *,
        username: str = ...,
        avatar: bytes | None = ...,
    ) -> UserData:
        payload = {}
        if username is not ...:
            payload['username'] = username
        if avatar is not ...:
            payload['avatar'] = avatar

        return await self.request('PATCH', Route('/users/@me'), payload)

    async def get_current_user_guilds(self) -> list[PartialGuildData]:
        return await self.request('GET', Route('/users/@me/guilds'), None)

    async def get_current_user_guild_member(self, guild_id: Snowflake) -> GuildMemberData:
        return await self.request('GET', Route('/users/@me/guilds/{guild_id}/member', guild_id=guild_id), None)

    async def leave_guild(self, guild_id: Snowflake) -> None:
        return await self.request('DELETE', Route('/users/@me/guilds/{guild_id}', guild_id=guild_id), None)

    async def create_dm(self, recipient_id: Snowflake) -> UserData:
        payload = {'recipient_id': recipient_id}

        return await self.request('POST', Route('/users/@me/channels'), payload)

    async def get_user_connections(self) -> list[ConnectionData]:
        return await self.request('GET', Route('/users/@me/connections'), None)
