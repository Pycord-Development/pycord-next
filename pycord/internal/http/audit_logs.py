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


from discord_typings import AuditLogData, AuditLogEvents, Snowflake

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class AuditLogRoutes(RouteCategoryMixin):
    async def get_guild_audit_log(
        self,
        guild_id: Snowflake,
        *,
        user_id: Snowflake | None = None,
        action_type: AuditLogEvents,
        before: Snowflake | None = None,
        limit: int | None = None,
    ) -> AuditLogData:
        params = {}
        if user_id is not None:
            params['user_id'] = user_id
        if action_type is not None:
            params['action_type'] = action_type.value
        if before is not None:
            params['before'] = before
        if limit is not None:
            params['limit'] = limit

        return await self.request('GET', Route('/guilds/{guild_id}/audit-logs', guild_id=guild_id), params=params)
