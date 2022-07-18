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


import datetime

from discord_typings import (
    GuildScheduledEventData,
    GuildScheduledEventEntityMetadata,
    GuildScheduledEventEntityTypes,
    GuildScheduledEventPrivacyLevels,
    GuildScheduledEventStatus,
    GuildScheduledEventUserData,
    Snowflake,
)

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class GuildScheduledEventRoutes(RouteCategoryMixin):
    async def list_scheduled_events_for_guild(
        self, guild_id: Snowflake, with_user_count: bool | None = None
    ) -> list[GuildScheduledEventData]:
        params = {}
        if with_user_count is not None:
            params['with_user_count'] = with_user_count

        return await self.request('GET', Route('/guilds/{guild_id}/scheduled-events', guild_id=guild_id), params=params)

    # TODO: image to `Asset`
    async def create_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        privacy_level: GuildScheduledEventPrivacyLevels,
        scheduled_start_time: datetime.datetime,
        entity_type: GuildScheduledEventEntityTypes,
        channel_id: Snowflake | None = None,
        entity_metadata: GuildScheduledEventEntityMetadata | None = None,
        scheduled_end_time: datetime.datetime | None = None,
        description: str | None = None,
        image: bytes | None = None,
        reason: str | None = None,
    ) -> GuildScheduledEventData:
        payload = {
            'name': name,
            'privacy_level': privacy_level.value,
            'scheduled_start_time': scheduled_start_time.isoformat(),
            'entity_type': entity_type.value,
        }

        if channel_id is not None:
            payload['channel_id'] = channel_id
        if entity_metadata is not None:
            payload['entity_metadata'] = entity_metadata
        if scheduled_end_time is not None:
            payload['scheduled_end_time'] = scheduled_end_time.isoformat()
        if description is not None:
            payload['description'] = description
        if image is not None:
            payload['image'] = image

        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/scheduled-events', guild_id=guild_id),
            payload,
            reason=reason
        )

    async def get_guild_scheduled_event(
        self, guild_id: Snowflake, event_id: Snowflake,
        *, with_user_count: bool | None = None
    ) -> GuildScheduledEventData:
        params = {}
        if with_user_count is not None:
            params['with_user_count'] = with_user_count

        return await self.request('GET', Route('/guilds/{guild_id}/scheduled-events/{event_id}', guild_id=guild_id,
                                               event_id=event_id), params=params)

    async def modify_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        event_id: Snowflake,
        *,
        channel_id: Snowflake | None = ...,
        entity_metadata: GuildScheduledEventEntityMetadata | None = ...,
        name: str = ...,
        privacy_level: GuildScheduledEventPrivacyLevels = ...,
        scheduled_start_time: datetime.datetime = ...,
        scheduled_end_time: datetime.datetime | None = ...,
        description: str | None = ...,
        entity_type: GuildScheduledEventEntityTypes = ...,
        status: GuildScheduledEventStatus = ...,
        image: bytes = ...,
        reason: str | None = None,
    ) -> GuildScheduledEventData:
        payload = {}
        if channel_id is not ...:
            payload['channel_id'] = channel_id
        if entity_metadata is not ...:
            payload['entity_metadata'] = entity_metadata
        if name is not ...:
            payload['name'] = name
        if privacy_level is not ...:
            payload['privacy_level'] = privacy_level.value
        if scheduled_start_time is not ...:
            payload['scheduled_start_time'] = scheduled_start_time.isoformat()
        if scheduled_end_time is not ...:
            payload['scheduled_end_time'] = scheduled_end_time.isoformat()
        if description is not ...:
            payload['description'] = description
        if entity_type is not ...:
            payload['entity_type'] = entity_type.value
        if status is not ...:
            payload['status'] = status.value
        if image is not ...:
            payload['image'] = image

        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/scheduled-events/{event_id}', guild_id=guild_id, event_id=event_id),
            payload,
            reason=reason
        )

    async def delete_guild_scheduled_event(self, guild_id: Snowflake, event_id: Snowflake) -> None:
        return await self.request('DELETE', Route('/guilds/{guild_id}/scheduled-events/{event_id}', guild_id=guild_id,
                                                  event_id=event_id))

    async def get_guild_scheduled_event_users(
        self,
        guild_id: Snowflake,
        event_id: Snowflake,
        *,
        limit: int | None = None,
        with_member: bool | None = None,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
    ) -> list[GuildScheduledEventUserData]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if with_member is not None:
            params['with_member'] = with_member
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after

        return await self.request('GET',
                                  Route('/guilds/{guild_id}/scheduled-events/{event_id}/users', guild_id=guild_id,
                                        event_id=event_id))
