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
from typing import Literal

from ...file import File
from ...snowflake import Snowflake
from ...types import GuildScheduledEvent, EntityMetadata, PRIVACY_LEVEL
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined, to_datauri
from ..route import Route
from .base import BaseRouter


class ScheduledEvents(BaseRouter):
    async def list_scheduled_events(self, guild_id: Snowflake, with_user_count: bool | UndefinedType = UNDEFINED) -> list[GuildScheduledEvent]:
        return await self.request(
            'GET',
            Route(
                '/guilds/{guild_id}/scheduled-events',
                guild_id=guild_id
            ),
            remove_undefined(with_user_count=with_user_count)
        )

    async def create_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        name: str,
        scheduled_start_time: str,
        entity_type: Literal[1, 2, 3],
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        entity_metadata: EntityMetadata | UndefinedType = UNDEFINED,
        privacy_level: PRIVACY_LEVEL | UndefinedType = UNDEFINED,
        scheduled_end_time: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        image: File | UndefinedType = UNDEFINED
    ) -> GuildScheduledEvent:
        fields = remove_undefined(
            name=name,
            scheduled_start_time=scheduled_start_time,
            entity_type=entity_type,
            channel_id=channel_id,
            entity_metadata=entity_metadata,
            privacy_level=privacy_level,
            scheduled_end_time=scheduled_end_time,
            description=description,
            image=image
        )

        if fields.get('image'):
            fields['image'] = to_datauri(fields['image'])

        # TODO
        await self.request(
            'POST',
            
        )
