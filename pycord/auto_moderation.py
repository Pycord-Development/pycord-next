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

from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import (
    AutoModActionType,
    AutoModEventType,
    AutoModKeywordPresetType,
    AutoModTriggerType,
)
from .snowflake import Snowflake
from .types import (
    AutoModerationAction as DiscordAutoModerationAction,
    AutoModerationActionMetadata as DiscordAutoModerationActionMetadata,
    AutoModerationRule as DiscordAutoModerationRule,
    AutoModerationTriggerMetadata as DiscordAutoModerationTriggerMetadata,
)
from .missing import MISSING, MissingEnum, Maybe

if TYPE_CHECKING:
    from .state import State


class AutoModTriggerMetadata:
    def __init__(self, data: DiscordAutoModerationTriggerMetadata) -> None:
        self.keyword_filter: list[str] | MissingEnum = data.get(
            'keyword_filter', MISSING
        )
        self.regex_patterns: list[str] | MissingEnum = data.get(
            'regex_patterns', MISSING
        )
        self.presets: list[AutoModKeywordPresetType] | MissingEnum = (
            [AutoModKeywordPresetType(preset) for preset in data['presets']]
            if data.get('presets') is not None
            else MISSING
        )
        self.allow_list: list[str] | MissingEnum = data.get('allow_list', MISSING)
        self.mention_total_limit: int | MissingEnum = data.get(
            'mention_total_limit', MISSING
        )


class AutoModActionMetadata:
    def __init__(self, data: DiscordAutoModerationActionMetadata) -> None:
        self.channel_id: Snowflake | MissingEnum = (
            Snowflake(data['channel_id'])
            if data.get('channel_id') is not None
            else MISSING
        )
        self.duration_seconds: int | MissingEnum = data.get(
            'duration_seconds', MISSING
        )


class AutoModAction:
    def __init__(self, data: DiscordAutoModerationAction) -> None:
        self.type: AutoModActionType = AutoModActionType(data['type'])
        self.metadata: AutoModActionMetadata = AutoModActionMetadata(data['metadata'])


class AutoModRule:
    def __init__(self, data: DiscordAutoModerationRule, state: State) -> None:
        self._state: State = state
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.name: str = data['name']
        self.creator_id: Snowflake = Snowflake(data['creator_id'])
        self.event_type: AutoModEventType = AutoModEventType(data['event_type'])
        self.trigger_type: AutoModTriggerType = AutoModTriggerType(data['trigger_type'])
        self.trigger_metadata: AutoModTriggerMetadata = AutoModTriggerMetadata(
            data['trigger_metadata']
        )
        self.actions: list[AutoModAction] = [
            AutoModAction(action) for action in data['actions']
        ]
        self.enabled: bool = data['enabled']
        self.exempt_roles: list[Snowflake] = [
            Snowflake(role) for role in data.get('exempt_roles', [])
        ]
        self.exempt_channels: list[Snowflake] = [
            Snowflake(member) for member in data.get('exempt_channels', [])
        ]

    async def edit(
        self,
        *,
        name: str | MissingEnum = MISSING,
        event_type: AutoModEventType | MissingEnum = MISSING,
        trigger_metadata: AutoModTriggerMetadata | MissingEnum = MISSING,
        actions: list[AutoModAction] | MissingEnum = MISSING,
        enabled: bool | MissingEnum = MISSING,
        exempt_roles: list[Snowflake] | MissingEnum = MISSING,
        exempt_channels: list[Snowflake] | MissingEnum = MISSING,
        reason: str | None = None,
    ) -> AutoModRule:
        """Edits the auto moderation rule.

        Parameters
        ----------
        name: :class:`str`
            The rule name.
        event_type: :class:`AutoModEventType`
            The event type.
        trigger_metadata: :class:`AutoModTriggerMetadata`
            The trigger metadata.
        actions: list[:class:`AutoModAction`]
            The actions to take when the rule is triggered.
        enabled: :class:`bool`
            Whether the rule is enabled.
        exempt_roles: list[:class:`Snowflake`]
            The roles exempt from the rule.
        exempt_channels: list[:class:`Snowflake`]
            The channels exempt from the rule.
        reason: :class:`str` | None
            The reason for editing this rule. Appears in the guild's audit log.
        """
        data = await self._state.http.modify_auto_moderation_rule(
            self.guild_id,
            self.id,
            name=name,
            event_type=event_type,
            trigger_metadata=trigger_metadata,
            actions=actions,
            enabled=enabled,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason,
        )
        return AutoModRule(data, self._state)

    async def delete(self, *, reason: str | None = None) -> None:
        """Deletes the auto moderation rule.

        Parameters
        ----------
        reason: :class:`str` | None
            The reason for deleting this rule. Appears in the guild's audit log.
        """
        await self._state.http.delete_auto_moderation_rule(
            self.guild_id, self.id, reason=reason
        )
