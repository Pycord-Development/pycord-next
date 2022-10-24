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


from discord_typings import Snowflake, StageInstanceData, StageInstancePrivacyLevels

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class StageInstanceRoutes(RouteCategoryMixin):
    async def create_stage_instance(
        self,
        *,
        channel_id: Snowflake,
        topic: str,
        privacy_level: StageInstancePrivacyLevels | None = None,
        send_start_notification: bool | None = None,
        reason: str | None = None,
    ) -> StageInstanceData:
        """Creates a new Stage instance associated to a Stage channel."""
        payload = {
            'channel_id': channel_id,
            'topic': topic,
        }
        if privacy_level is not None:
            payload['privacy_level'] = privacy_level
        if send_start_notification is not None:
            payload['send_start_notification'] = send_start_notification

        return await self.request(
            'POST',
            Route('/stage-instances'),
            payload,
            reason=reason,
        )

    async def get_stage_instance(self, channel_id: Snowflake) -> StageInstanceData:
        """Gets the stage instance associated with the Stage channel, if it exists."""
        return await self.request('GET', Route('/stage-instances/{channel_id}', channel_id=channel_id))

    async def modify_stage_instance(
        self,
        channel_id: Snowflake,
        *,
        topic: str = ...,
        privacy_level: StageInstancePrivacyLevels = ...,
        reason: str | None = None,
    ) -> StageInstanceData:
        """Updates fields of an existing Stage instance."""
        payload = {}
        if topic is not ...:
            payload['topic'] = topic
        if privacy_level is not ...:
            payload['privacy_level'] = privacy_level

        return await self.request(
            'PATCH',
            Route('/stage-instances/{channel_id}', channel_id=channel_id),
            payload,
            reason=reason,
        )

    async def delete_stage_instance(self, channel_id: Snowflake, reason: str | None = None) -> None:
        """Deletes the Stage instance."""
        await self.request('DELETE', Route('/stage-instances/{channel_id}', channel_id=channel_id), reason=reason)
