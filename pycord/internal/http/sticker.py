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
from aiohttp import FormData
from discord_typings import Snowflake, StickerData, StickerPackData

from pycord import File
from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin
from pycord.types import ListNitroStickerPacksData


class StickerRoutes(RouteCategoryMixin):
    async def get_sticker(self, sticker_id: Snowflake) -> dict:
        """Returns a sticker for the given sticker ID."""
        return await self.request('GET', Route('/stickers/{sticker_id}', sticker_id=sticker_id))

    async def list_nitro_sticker_packs(self) -> list[StickerPackData]:
        """Returns the list of sticker packs available to Nitro subscribers."""
        val: ListNitroStickerPacksData = await self.request('GET', Route('/sticker-packs'))
        return val['sticker_packs']

    async def list_guild_stickers(self, guild_id: Snowflake) -> list[StickerData]:
        """Returns a list of stickers for the given guild."""
        return await self.request('GET', Route('/guilds/{guild_id}/stickers', guild_id=guild_id))

    async def get_guild_sticker(self, guild_id: Snowflake, sticker_id: Snowflake) -> StickerData:
        """Returns a sticker for the given guild and sticker IDs."""
        return await self.request('GET', Route('/guilds/{guild_id}/stickers/{sticker_id}', guild_id=guild_id,
                                               sticker_id=sticker_id))

    # TODO: file to `Asset` or something special
    # FIXME: Untested
    async def create_guild_sticker(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        description: str,
        tags: str,
        file: File,
        reason: str | None = None,
    ) -> StickerData:
        """Create a new sticker for the guild."""
        form_data = FormData(quote_fields=False)
        form_data.add_field(name='name', value=name)
        form_data.add_field(name='description', value=description)
        form_data.add_field(name='tags', value=tags)
        form_data.add_field(name='file', value=file.fp, content_type='application/octet-stream', filename=file.filename)

        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/stickers', guild_id=guild_id),
            form_data,
            reason=reason,
        )

    async def modify_guild_sticker(
        self,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        name: str = ...,
        description: str = ...,
        tags: str = ...,
        reason: str | None = None,
    ) -> StickerData:
        """Modify the given sticker."""
        payload = {}
        if name is not ...:
            payload['name'] = name
        if description is not ...:
            payload['description'] = description
        if tags is not ...:
            payload['tags'] = tags

        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/stickers/{sticker_id}', guild_id=guild_id, sticker_id=sticker_id),
            payload,
            reason=reason,
        )

    async def delete_guild_sticker(self, guild_id: Snowflake, sticker_id: Snowflake, reason: str | None = None) -> None:
        """Delete the given sticker."""
        await self.request('DELETE',
                           Route('/guilds/{guild_id}/stickers/{sticker_id}', guild_id=guild_id, sticker_id=sticker_id),
                           reason=reason)
