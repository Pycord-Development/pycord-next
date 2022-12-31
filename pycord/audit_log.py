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

from typing import TYPE_CHECKING, Any

from .auto_moderation import AutoModRule
from .channel import Thread
from .enums import AuditLogEvent
from .integration import Integration
from .scheduled_event import ScheduledEvent
from .snowflake import Snowflake
from .types import (
    ApplicationCommand as DiscordApplicationCommand,
    AuditLog as DiscordAuditLog,
    AuditLogChange as DiscordAuditLogChange,
    AuditLogEntry as DiscordAuditLogEntry,
    OptionalAuditEntryInfo as DiscordOptionalAuditEntryInfo,
)
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .webhook import GuildWebhook

if TYPE_CHECKING:
    from .state import State


class OptionalAuditEntryInfo:
    """
    Represents Optionalized Audit Log Information.

    Attributes
    ----------
    application_id: :class:`.snowflake.Snowflake` | :class:`.undefined.UndefinedType`
    auto_moderation_rule_name: :class:`str` | :class:`.undefined.UndefinedType`
    auto_moderation_rule_trigger_type: :class:`str` | :class:`.undefined.UndefinedType`
    channel_id: :class:`.snowflake.Snowflake` | :class:`.undefined.UndefinedType`
    count: :class:`int` | :class:`.undefined.UndefinedType`
    delete_member_days: :class:`int` | :class:`.undefined.UndefinedType`
    id: :class:`Snowflake` | :class:`.undefined.UndefinedType`
    members_removed: :class:`int` | :class:`.undefined.UndefinedType`
    message_id: :class:`Snowflake` | :class:`.undefined.UndefinedType`
    role_name: :class:`str` | :class:`.undefined.UndefinedType`
    type: :class:`int` | :class:`.undefined.UndefinedType`
    """

    def __init__(self, data: DiscordOptionalAuditEntryInfo) -> None:
        self.application_id: Snowflake | UndefinedType = (
            Snowflake(data['application_id']) if 'application_id' in data else UNDEFINED
        )
        self.auto_moderation_rule_name: str | UndefinedType = data.get(
            'auto_moderation_rule_name', UNDEFINED
        )
        self.auto_moderation_rule_trigger_type: str | UndefinedType = data.get(
            'auto_moderation_rule_trigger_type', UNDEFINED
        )
        self.channel_id: Snowflake | UndefinedType = (
            Snowflake(data['channel_id']) if 'channel_id' in data else UNDEFINED
        )
        self.count: int | UndefinedType = (
            int(data['count']) if 'count' in data else UNDEFINED
        )
        self.delete_member_days: int | UndefinedType = (
            int(data['delete_member_days'])
            if 'delete_member_days' in data
            else UNDEFINED
        )
        self.id: Snowflake | UndefinedType = (
            Snowflake(data['id']) if 'id' in data else UNDEFINED
        )
        self.members_removed: int | UndefinedType = (
            int(data['members_removed']) if 'members_removed' in data else UNDEFINED
        )
        self.message_id: Snowflake | UndefinedType = (
            Snowflake(data['message_id']) if 'message_id' in data else UNDEFINED
        )
        self.role_name: str | UndefinedType = data.get('role_name', UNDEFINED)
        self.type: int | UndefinedType = (
            int(data['type']) if 'type' in data else UNDEFINED
        )


class AuditLogChange:
    """
    Represents an Audit Log Change

    Attributes
    ----------
    key: :class:`str`
    new_value: Any | :class:`.undefined.UndefinedType`
    old_value: Any | :class:`.undefined.UndefinedType`
    """

    def __init__(self, data: DiscordAuditLogChange) -> None:
        self.key: str = data['key']
        self.new_value: Any | UndefinedType = data.get('new_value', UNDEFINED)
        self.old_value: Any | UndefinedType = data.get('old_value', UNDEFINED)


class AuditLogEntry:
    """
    Represents an entry into the Audit Log

    Attributes
    ----------
    id: :class:`.snowflake.Snowflake`
    target_id: :class:`.snowflake.Snowflake` | :class:`.undefined.UndefinedType`
    user_id: :class:`.snowflake.Snowflake` | :class:`.undefined.UndefinedType`
    action_type: :class:`.audit_log.AuditLogEvent`
    options: :class:`.audit_log.OptionalAuditEntryInfo` | :class:`.undefined.UndefinedType`
    reason: :class:`str` | :class:`.undefined.UndefinedType`
    """

    def __init__(self, data: DiscordAuditLogEntry) -> None:
        self.target_id: Snowflake | UndefinedType = (
            Snowflake(data['target_id']) if data['target_id'] is not None else UNDEFINED
        )
        self._changes: list[AuditLogChange] = [
            AuditLogChange(change) for change in data.get('changes', [])
        ]
        self.user_id: Snowflake | UndefinedType = (
            Snowflake(data['user_id']) if data['user_id'] is not None else UNDEFINED
        )

        self.id: Snowflake = Snowflake(data['id'])
        self.action_type: AuditLogEvent = AuditLogEvent(data['action_type'])
        self.options: OptionalAuditEntryInfo | UndefinedType = (
            OptionalAuditEntryInfo(data['options'])
            if data.get('options') is not None
            else UNDEFINED
        )
        self.reason: str | UndefinedType = data.get('reason', UNDEFINED)


class AuditLog:
    """
    Represents an Audit Log inside a Guild

    Attributes
    ----------
    audit_log_entries: list[:class:`.audit_log.AuditLogEntry`]
    auto_moderation_rules: list[:class:`.auto_moderation.AutoModRule`]
    guild_scheduled_events: list[:class:`.scheduled_event.ScheduledEvent`]
    integrations: list[:class:`.user.Integration`]
    users: list[:class:`.user.User`]
    webhooks: list[:class:`.webhook.GuildWebhook`]
    """

    def __init__(self, data: DiscordAuditLog, state: State) -> None:
        # TODO: use models for these
        self._application_commands: list[DiscordApplicationCommand] = data[
            'application_commands'
        ]
        self.audit_log_entries: list[AuditLogEntry] = [
            AuditLogEntry(entry) for entry in data['audit_log_entries']
        ]
        self.auto_moderation_rules: list[AutoModRule] = [
            AutoModRule(rule, state) for rule in data['auto_moderation_rules']
        ]
        self.guild_scheduled_events: list[ScheduledEvent] = [
            ScheduledEvent(event, state) for event in data['guild_scheduled_events']
        ]
        self.integrations: list[Integration] = [
            Integration(i) for i in data.get('integrations', [])
        ]
        self.threads: list[Thread] = [
            Thread(thread, state) for thread in data['threads']
        ]
        self.users: list[User] = [User(user, state) for user in data['users']]
        self.webhooks: list[GuildWebhook] = [
            GuildWebhook(w, state) for w in data['webhooks']
        ]
