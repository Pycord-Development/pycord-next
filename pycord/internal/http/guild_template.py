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
from discord_typings import GuildData, GuildTemplateData, Snowflake

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin
from pycord.utils import _convert_base64_from_bytes


class GuildTemplateRoutes(RouteCategoryMixin):
    async def get_guild_template(self, template_code: str) -> GuildTemplateData:
        return await self.request('GET', Route('/guilds/templates/{template_code}', template_code=template_code))

    async def create_guild_from_guild_template(
        self,
        template_code: str,
        *,
        name: str,
        icon: bytes | None = None,
    ) -> GuildData:
        payload = {'name': name}
        if icon is not None:
            payload['icon'] = _convert_base64_from_bytes(icon)

        return await self.request(
            'POST',
            Route('/guilds/templates/{template_code}/guilds', template_code=template_code),
            payload
        )

    async def get_guild_templates(self, guild_id: Snowflake) -> list[GuildTemplateData]:
        return await self.request('GET', Route('/guilds/{guild_id}/templates', guild_id=guild_id))

    async def create_guild_template(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        description: str | None = None,
    ) -> GuildTemplateData:
        payload = {'name': name}
        if description is not None:
            payload['description'] = description

        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/templates', guild_id=guild_id),
            payload
        )

    async def sync_guild_template(self, guild_id: Snowflake, template_code: str) -> GuildTemplateData:
        return await self.request('PUT', Route('/guilds/{guild_id}/templates/{template_code}', guild_id,
                                               template_code=template_code))

    async def modify_guild_template(
        self,
        guild_id: Snowflake,
        template_code: str,
        *,
        name: str = ...,
        description: str | None = ...,
    ) -> GuildTemplateData:
        payload = {}
        if name is not ...:
            payload['name'] = name
        if description is not ...:
            payload['description'] = description

        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/templates/{template_code}', guild_id, template_code=template_code),
            payload
        )

    async def delete_guild_template(self, guild_id: Snowflake, template_code: str) -> None:
        return await self.request('DELETE', Route('/guilds/{guild_id}/templates/{template_code}', guild_id,
                                                  template_code=template_code))
