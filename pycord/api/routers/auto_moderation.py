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
from ...snowflake import Snowflake
from ...types import (
    AutoModerationRule, 
    AutoModerationTriggerMetadata, 
    AutoModerationAction,
    AUTO_MODERATION_EVENT_TYPES, 
    AUTO_MODERATION_TRIGGER_TYPES,
)
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined
from ..route import Route
from .base import BaseRouter


class AutoModeration(BaseRouter):
    async def list_auto_moderation_rules_for_guild(
        self, guild_id: Snowflake
    ) -> list[AutoModerationRule]:
        return await self.request(
            'GET',
            Route(
                '/guilds/{guild_id}/auto-moderation/rules', guild_id=guild_id,
            ),
        )
    
    async def get_auto_moderation_rule(
        self, guild_id: Snowflake, rule_id: Snowflake,
    ) -> AutoModerationRule:
        return await self.request(
            'GET',
            Route(
                '/guilds/{guild_id}/auto-moderation/rules/{rule_id}', guild_id=guild_id, rule_id=rule_id,
            )
        )
    
    async def create_auto_moderation_rule(
        self, guild_id: Snowflake, *,
        name: str, 
        event_type: AUTO_MODERATION_EVENT_TYPES,
        trigger_type: AUTO_MODERATION_TRIGGER_TYPES,
        actions: list[AutoModerationAction],
        trigger_metadata: AutoModerationTriggerMetadata | UndefinedType = UNDEFINED,
        enabled: bool = False,
        exempt_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        exempt_channels: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> AutoModerationRule:
        data = {
            "name": name,
            "event_type": event_type,
            "trigger_type": trigger_type,
            "trigger_metadata": trigger_metadata,
            "actions": actions,
            "enabled": enabled,
            "exampt_roles": exempt_roles,
            "exempt_channels": exempt_channels,
        }
        return await self.request(
            'POST',
            Route(
                '/guilds/{guild_id}/auto-moderation/rules', guild_id=guild_id,
            ),
            remove_undefined(data),
            reason=reason,
        )
    
    async def modify_auto_moderation_rule(
        self, guild_id: Snowflake, rule_id: Snowflake, *,
        name: str | UndefinedType = UNDEFINED, 
        event_type: AUTO_MODERATION_EVENT_TYPES | UndefinedType = UNDEFINED,
        trigger_type: AUTO_MODERATION_TRIGGER_TYPES | UndefinedType = UNDEFINED,
        actions: list[AutoModerationAction] | UndefinedType = UNDEFINED,
        trigger_metadata: AutoModerationTriggerMetadata | UndefinedType | None = UNDEFINED,
        enabled: bool | UndefinedType = UNDEFINED,
        exempt_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        exempt_channels: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | None = None,
    ) -> AutoModerationRule:
        data = {
            "name": name,
            "event_type": event_type,
            "trigger_type": trigger_type,
            "trigger_metadata": trigger_metadata,
            "actions": actions,
            "enabled": enabled,
            "exampt_roles": exempt_roles,
            "exempt_channels": exempt_channels,
        }
        return await self.request(
            'PATCH',
            Route(
                '/guilds/{guild_id}/auto-moderation/rules/{rule_id}', guild_id=guild_id, rule_id=rule_id,
            ),
            remove_undefined(data),
            reason=reason,
        )
    
    async def delete_auto_moderation_rule(
        self, guild_id: Snowflake, rule_id: Snowflake, *, reason: str | None = None
    ) -> None:
        return await self.request(
            'DELETE',
            Route(
                '/guilds/{guild_id}/auto-moderation/rules/{rule_id}', guild_id=guild_id, rule_id=rule_id,
            ),
            reason=reason,
        )

