# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
# Copyright (c) 2022-present Pycord Development
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

from .enums import AutoModActionType, AutoModEventType, AutoModKeywordPresetType, AutoModTriggerType
from .snowflake import Snowflake
from .types import (
    AutoModerationAction as DiscordAutoModerationAction,
    AutoModerationActionMetadata as DiscordAutoModerationActionMetadata,
    AutoModerationRule as DiscordAutoModerationRule,
    AutoModerationTriggerMetadata as DiscordAutoModerationTriggerMetadata,
)
from .utils import UNDEFINED, UndefinedType

if TYPE_CHECKING:
    from .state import State


class AutoModTriggerMetadata:
    def __init__(self, data: DiscordAutoModerationTriggerMetadata) -> None:
        self.keyword_filter: list[str] | UndefinedType = data.get('keyword_filter', UNDEFINED)
        self.regex_patterns: list[str] | UndefinedType = data.get('regex_patterns', UNDEFINED)
        self.presets: list[AutoModKeywordPresetType] | UndefinedType = (
            [AutoModKeywordPresetType(preset) for preset in data['presets']]
            if data.get('presets') is not None else UNDEFINED
        )
        self.allow_list: list[str] | UndefinedType = data.get('allow_list', UNDEFINED)
        self.mention_total_limit: int | UndefinedType = data.get('mention_total_limit', UNDEFINED)


class AutoModActionMetadata:
    def __init__(self, data: DiscordAutoModerationActionMetadata) -> None:
        self.channel_id: Snowflake | UndefinedType = (
            Snowflake(data['channel_id']) if data.get('channel_id') is not None else UNDEFINED
        )
        self.duration_seconds: int | UndefinedType = data.get('duration_seconds', UNDEFINED)


class AutoModAction:
    def __init__(self, data: DiscordAutoModerationAction) -> None:
        self.type: AutoModActionType = AutoModActionType(data['type'])
        self.metadata: AutoModActionMetadata = AutoModActionMetadata(data['metadata'])


class AutoModRule:
    def __init__(self, data: DiscordAutoModerationRule, state: State):
        self.id: Snowflake = Snowflake(data['id'])
        self.guild_id: Snowflake = Snowflake(data['guild_id'])
        self.name: str = data['name']
        self.creator_id: Snowflake = Snowflake(data['creator_id'])
        self.event_type: AutoModEventType = AutoModEventType(data['event_type'])
        self.trigger_type: AutoModTriggerType = AutoModTriggerType(data['trigger_type'])
        self.trigger_metadata: AutoModTriggerMetadata = AutoModTriggerMetadata(data['trigger_metadata'])
        self.actions: list[AutoModAction] = [AutoModAction(action) for action in data['actions']]
        self.enabled: bool = data['enabled']
        self.exempt_roles: list[Snowflake] = [Snowflake(role) for role in data.get('exempt_roles', [])]
        self.exempt_channels: list[Snowflake] = [Snowflake(member) for member in data.get('exempt_channels', [])]
