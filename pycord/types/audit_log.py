# cython: language_level=3
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

from typing import Any, Literal

from typing_extensions import NotRequired, TypedDict

from .application_commands import ApplicationCommand
from .auto_moderation import AutoModerationRule
from .channel import Channel
from .guild_scheduled_event import GuildScheduledEvent
from .integration import Integration
from .snowflake import Snowflake
from .user import User
from .webhook import Webhook

AUDIT_LOG_EVENT_TYPE = Literal[
    1,
    10,
    11,
    12,
    13,
    14,
    15,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    30,
    31,
    32,
    40,
    41,
    42,
    50,
    51,
    52,
    60,
    61,
    62,
    72,
    73,
    74,
    75,
    80,
    81,
    82,
    83,
    84,
    85,
    90,
    91,
    92,
    100,
    101,
    102,
    110,
    111,
    112,
    121,
    140,
    141,
    142,
    143,
    144,
    145,
]


class AuditLogChange(TypedDict):
    new_value: NotRequired[Any]
    old_value: NotRequired[Any]
    key: str


class OptionalAuditEntryInfo(TypedDict):
    application_id: Snowflake
    auto_moderation_rule_name: str
    auto_moderation_rule_trigger_type: str
    channel_id: Snowflake
    count: str
    delete_member_days: str
    id: Snowflake
    members_removed: str
    message_id: Snowflake
    role_name: str
    type: str


class AuditLogEntry(TypedDict):
    target_id: str | None
    changes: NotRequired[AuditLogChange]
    user_id: Snowflake | None
    id: Snowflake
    action_type: AUDIT_LOG_EVENT_TYPE
    options: NotRequired[OptionalAuditEntryInfo]
    reason: NotRequired[str]


class AuditLog(TypedDict):
    application_commands: list[ApplicationCommand]
    audit_log_entries: list[AuditLogEntry]
    auto_moderation_rules: list[AutoModerationRule]
    guild_scheduled_events: list[GuildScheduledEvent]
    integrations: list[Integration]
    threads: list[Channel]
    users: list[User]
    webhooks: list[Webhook]
