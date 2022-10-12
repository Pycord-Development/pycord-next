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


from discord_typings import (
    AutoModerationActionData,
    AutoModerationEventTypes,
    AutoModerationRuleData,
    AutoModerationTriggerMetadataData,
    AutoModerationTriggerTypes,
    Snowflake,
)

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class AutoModerationRoutes(RouteCategoryMixin):
    async def list_auto_moderation_rules_for_guild(self, guild_id: Snowflake) -> list[AutoModerationRuleData]:
        """Get a list of all rules currently configured for the guild. Returns a list of auto moderation rule objects."""
        return await self.request('GET', Route('/guilds/{guild_id}/automod-rules', guild_id=guild_id))

    async def get_auto_moderation_rule(self, guild_id: Snowflake, rule_id: Snowflake) -> AutoModerationRuleData:
        """Get a single rule. Returns an auto moderation rule."""
        return await self.request('GET', Route('/guilds/{guild_id}/automod-rules/{rule_id}', guild_id=guild_id,
                                               rule_id=rule_id))

    async def create_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        event_type: AutoModerationEventTypes,
        trigger_type: AutoModerationTriggerTypes,
        actions: list[AutoModerationActionData],
        trigger_metadata: AutoModerationTriggerMetadataData | None = None,
        enabled: bool | None = None,
        exempt_roles: list[Snowflake] | None = None,
        exempt_channels: list[Snowflake] | None = None,
        reason: str | None = None,
    ) -> AutoModerationRuleData:
        """Create a new rule. Returns an auto moderation rule on success. Fires an Auto Moderation Rule Create Gateway event."""
        payload = {
            'name': name,
            'event_type': event_type.value,
            'trigger_type': trigger_type.value,
            'actions': actions,
        }

        if trigger_metadata is not None:
            payload['trigger_metadata'] = trigger_metadata
        if enabled is not None:
            payload['enabled'] = enabled
        if exempt_roles is not None:
            payload['exempt_roles'] = exempt_roles
        if exempt_channels is not None:
            payload['exempt_channels'] = exempt_channels

        return await self.request(
            'POST',
            Route('/guilds/{guild_id}/automod-rules', guild_id=guild_id),
            payload,
            reason=reason
        )

    async def modify_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        rule_id: Snowflake,
        *,
        name: str = ...,
        event_type: AutoModerationEventTypes = ...,
        trigger_metadata: AutoModerationTriggerMetadataData = ...,
        actions: list[AutoModerationActionData] = ...,
        enabled: bool = ...,
        exempt_roles: list[Snowflake] = ...,
        exempt_channels: list[Snowflake] = ...,
        reason: str | None = None,
    ) -> AutoModerationRuleData:
        """Modify an existing rule. Returns an auto moderation rule on success. Fires an Auto Moderation Rule Update Gateway event."""
        payload = {}
        if name is not ...:
            payload['name'] = name
        if event_type is not ...:
            payload['event_type'] = event_type
        if trigger_metadata is not ...:
            payload['trigger_metadata'] = trigger_metadata
        if actions is not ...:
            payload['actions'] = actions
        if enabled is not ...:
            payload['enabled'] = enabled
        if exempt_roles is not ...:
            payload['exempt_roles'] = exempt_roles
        if exempt_channels is not ...:
            payload['exempt_channels'] = exempt_channels

        return await self.request(
            'PATCH',
            Route('/guilds/{guild_id}/automod-rules/{rule_id}', guild_id=guild_id, rule_id=rule_id),
            payload,
            reason=reason
        )

    async def delete_auto_moderation_rule(
        self, guild_id: Snowflake, rule_id: Snowflake, reason: str | None = None
    ) -> None:
        """Delete a rule. Fires an Auto Moderation Rule Delete Gateway event."""
        return await self.request('DELETE', Route('/guilds/{guild_id}/automod-rules/{rule_id}', guild_id=guild_id,
                                                  rule_id=rule_id), reason=reason)
