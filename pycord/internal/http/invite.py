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


from discord_typings import InviteData, Snowflake

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class InviteRoutes(RouteCategoryMixin):
    async def get_invite(
        self,
        invite_code: str,
        *,
        with_counts: bool | None = None,
        with_expiration: bool | None = None,
        guild_scheduled_event_id: Snowflake | None = None,
    ) -> InviteData:
        params = {}
        if with_counts is not None:
            params['with_counts'] = with_counts
        if with_expiration is not None:
            params['with_expiration'] = with_expiration
        if guild_scheduled_event_id is not None:
            params['guild_scheduled_event_id'] = guild_scheduled_event_id

        return await self.request(
            'GET',
            Route('/invites/{invite_code}', invite_code=invite_code),
            params=params
        )

    async def delete_invite(self, invite_code: str, *, reason: str | None = None) -> None:
        return await self.request('DELETE', Route('/invites/{invite_code}', invite_code=invite_code), reason=reason)
