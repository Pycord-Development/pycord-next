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

# ah! we've been cursed!
# from curses import meta

from __future__ import annotations

import datetime

from .enums import AutoModEventType, AutoModTriggerType, AutoModActionType, AutoModKeywordPresetType
from .mixins import Identifiable
from .missing import Maybe, MISSING

from typing import Any, Type, TYPE_CHECKING, Self, Union

if TYPE_CHECKING:
    from discord_typings import (
        AutoModerationRuleData,
        KeywordAutoModerationTriggerMetadata as KeywordAutoModerationTriggerMetadataData,
        AutoModerationTriggerMetadataData,
        KeywordPresetAutoModerationTriggerMetadataData,
        MentionSpamAutoModerationTriggerMetadataData,
        AutoModerationActionMetadataData,
        TimeoutAutoModerationActionMetadataData,
        BlockmessageAutoModerationActionMetadataData,
        SendAlertMessageAutoModerationActionMetadataData,
        AutoModerationActionData as AutoModerationActionData,
    )
    from .guild import Guild
    from .mixins import Snowflake
    from .state import State

__all__ = (
    "AutoModRule",
    "AutoModTriggerMetadata",
    "KeywordAutoModTriggerMetadata",
    "KeywordPresetAutoModTriggerMetadata",
    "MentionSpamAutoModTriggerMetadata",
    "AutoModAction",
    "AutoModActionMetadata",
    "TimeoutAutoModActionMetadata",
    "BlockMessageAutoModActionMetadata",
    "SendAlertMessageAutoModActionMetadata",
)


class AutoModRule(Identifiable):
    """
    Represents an auto moderation rule.

    Attributes
    ----------
    id: :class:`int`
        The rule's ID.
    guild_id: :class:`int`
        The ID of the guild this rule is in.
    name: :class:`str`
        The rule's name.
    creator_id: :class:`int`
        The ID of the user who created this rule.
    event_type: :class:`AutoModEventType`
        The type of event this rule is for.
    trigger_type: :class:`AutoModTriggerType`
        The trigger type used by this rule.
    trigger_metadata: :class:`AutoModTriggerMetadata`
        The metadata for the trigger. Type corresponds to the trigger type.
    actions: list[:class:`AutoModAction`]
        The actions to take when this rule is triggered.
    enabled: :class:`bool`
        Whether or not this rule is enabled.
    exempt_role_ids: list[:class:`int`]
        The roles that are exempt from this rule.
    exempt_channel_ids: list[:class:`int`]
        The channels that are exempt from this rule.
    """
    __slots__ = (
        "_state",
        "id",
        "guild_id",
        "name",
        "creator_id",
        "event_type",
        "trigger_type",
        "trigger_metadata",
        "actions",
        "enabled",
        "exempt_role_ids",
        "exempt_channel_ids",
    )

    def __init__(self, data: AutoModerationRuleData, state: State) -> None:
        self._state: State = state
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.name: str = data["name"]
        self.creator_id: int = int(data["creator_id"])
        self.event_type: AutoModEventType = AutoModEventType(data["event_type"])
        self.trigger_type: AutoModTriggerType = AutoModTriggerType(data["trigger_type"])
        self.trigger_metadata: Maybe[AutoModTriggerMetadata] = trigger_metadata_factory(data)
        self.actions: list[AutoModAction] = [AutoModAction.from_data(x) for x in data["actions"]]
        self.enabled: bool = data["enabled"]
        self.exempt_role_ids: list[int] = [int(x) for x in data["exempt_roles"]]
        self.exempt_channel_ids: list[int] = [int(x) for x in data["exempt_channels"]]

    def __repr__(self) -> str:
        return f"<AutoModRule id={self.id} name={self.name!r} event_type={self.event_type} trigger_type={self.trigger_type} creator_id={self.creator_id} enabled={self.enabled}>"

    def __str__(self) -> str:
        return self.name

    @property
    def guild(self) -> Guild:
        # TODO: fetch from cache
        raise NotImplementedError

    async def modify(
        self,
        *,
        name: Maybe[str] = MISSING,
        trigger_type: Maybe[AutoModTriggerType] = MISSING,
        trigger_metadata: Maybe[AutoModTriggerMetadata] = MISSING,
        actions: Maybe[list[AutoModAction]] = MISSING,
        enabled: Maybe[bool] = MISSING,
        exempt_roles: Maybe[list[Snowflake]] = MISSING,
        exempt_channels: Maybe[list[Snowflake]] = MISSING,
        reason: Maybe[str] = MISSING,
    ) -> AutoModRule:
        """
        Modifies this rule.

        Parameters
        ----------
        name: :class:`str`
            The new name for this rule.
        trigger_type: :class:`AutoModTriggerType`
            The new trigger type for this rule.
        trigger_metadata: :class:`AutoModTriggerMetadata`
            The new trigger metadata for this rule.
        actions: list[:class:`AutoModAction`]
            The new actions for this rule.
        enabled: :class:`bool`
            Whether or not this rule is enabled.
        exempt_roles: list[:class:`.Snowflake`]
            The roles that are exempt from this rule.
        exempt_channels: list[:class:`.Snowflake`]
            The channels that are exempt from this rule.
        reason: :class:`str`
            The reason for modifying this rule. Shows up in the audit log.

        Returns
        -------
        :class:`AutoModRule`
            The modified rule.

        Raises
        ------
        :exc:`.Forbidden`
            You do not have permission to modify this rule.
        :exc:`.NotFound`
            The rule was not found, it may have been deleted.
        :exc:`.HTTPException`
            Modifying the rule failed.
        """
        payload = {
            "name": name,
            "trigger_type": trigger_type,
            "trigger_metadata": trigger_metadata,
            "actions": actions,
            "enabled": enabled,
            "exempt_roles": [x.id for x in exempt_roles] if exempt_roles else MISSING,
            "exempt_channels": [x.id for x in exempt_channels] if exempt_channels else MISSING,
        }
        return await self._state.http.modify_auto_moderation_rule(self.guild_id, self.id, **payload, reason=reason)

    async def delete(self, *, reason: Maybe[str]) -> None:
        """
        Deletes this rule.

        Parameters
        ----------
        reason: :class:`str`
            The reason for deleting this rule. Shows up in the audit log.

        Raises
        ------
        :exc:`.Forbidden`
            You do not have permission to delete this rule.
        :exc:`.NotFound`
            The rule was not found, it may have already been deleted.
        :exc:`.HTTPException`
            Deleting the rule failed.
        """
        return await self._state.http.delete_auto_moderation_rule(self.guild_id, self.id, reason=reason)


class _BaseTriggerMetadata:
    @classmethod
    def from_data(cls: Type[AutoModTriggerMetadata], data: AutoModerationTriggerMetadataData) -> AutoModTriggerMetadata:
        return cls(**data)

    def to_data(self) -> AutoModerationTriggerMetadataData:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {''.join([f'{k}={v!r}' for k, v in self.__dict__.items()])}>"


class KeywordAutoModTriggerMetadata(_BaseTriggerMetadata):
    """
    Represents the metadata for a trigger of type :attr:`.AutoModTriggerType.KEYWORD`.

    Attributes
    ----------
    keyword_filter: list[:class:`str`]
        The keywords to filter.
    regex_patterns: list[:class:`str`]
        The regex patterns to filter.
    allow_list: list[:class:`str`]
        The list of words to allow.
    """
    __slots__ = ("keyword_filter", "regex_patterns", "allow_list")

    def __init__(
        self,
        *,
        keyword_filter: list[str],
        regex_patterns: list[str],
        allow_list: list[str],
    ) -> None:
        self.keyword_filter: list[str] = keyword_filter
        self.regex_patterns: list[str] = regex_patterns
        self.allow_list: list[str] = allow_list

    def to_data(self) -> KeywordAutoModerationTriggerMetadataData:
        return {
            "keyword_filter": self.keyword_filter,
            "regex_patterns": self.regex_patterns,
            "allow_list": self.allow_list,
        }


class KeywordPresetAutoModTriggerMetadata(_BaseTriggerMetadata):
    """
    Represents the metadata for a trigger of type :attr:`.AutoModTriggerType.KEYWORD_PRESET`.

    Attributes
    ----------
    presets: list[:class:`.AutoModKeywordPresetType`]
        The presets to use.
    allow_list: list[:class:`str`]
        The list of words to allow.
    """
    __slots__ = ("presets", "allow_list")

    def __init__(
        self,
        *,
        presets: list[AutoModKeywordPresetType],
        allow_list: list[str],
    ) -> None:
        self.presets: list[AutoModKeywordPresetType] = presets
        self.allow_list: list[str] = allow_list

    def to_data(self) -> KeywordPresetAutoModerationTriggerMetadataData:
        return {
            "presets": [x.value for x in self.presets],
            "allow_list": self.allow_list,
        }


class MentionSpamAutoModTriggerMetadata(_BaseTriggerMetadata):
    """
    Represents the metadata for a trigger of type :attr:`.AutoModTriggerType.MENTION_SPAM`.

    Attributes
    ----------
    mention_total_limit: :class:`int`
        The number of mentions that can be sent before triggering the rule.
    mention_raid_protection_enabled: :class:`bool`
        Whether or not raid protection is enabled.
    """
    __slots__ = ("mention_total_limit", "mention_raid_protection_enabled")

    def __init__(
        self,
        *,
        mention_total_limit: int,
        mention_raid_protection_enabled: bool,
    ) -> None:
        self.mention_total_limit: int = mention_total_limit
        self.mention_raid_protection_enabled: bool = mention_raid_protection_enabled

    def to_data(self) -> "MentionSpamAutoModerationTriggerMetadataData":
        return {
            "mention_total_limit": self.mention_total_limit,
            "mention_raid_protection_enabled": self.mention_raid_protection_enabled,
        }


AutoModTriggerMetadata = Union[
    KeywordAutoModTriggerMetadata,
    KeywordPresetAutoModTriggerMetadata,
    MentionSpamAutoModTriggerMetadata,
]


def trigger_metadata_factory(data: "AutoModerationRuleData") -> AutoModTriggerMetadata:
    trigger_type = AutoModTriggerType(data["trigger_type"])
    return {
        AutoModTriggerType.KEYWORD: KeywordAutoModTriggerMetadata,
        AutoModTriggerType.KEYWORD_PRESET: KeywordPresetAutoModTriggerMetadata,
        AutoModTriggerType.MENTION_SPAM: MentionSpamAutoModTriggerMetadata,
    }[trigger_type].from_data(data["trigger_metadata"])


class AutoModAction:
    """
    Represents an auto moderation action.

    Attributes
    ----------
    type: :class:`AutoModActionType`
        The type of action.
    metadata: :class:`AutoModActionMetadata`
        The metadata for the action.
    """

    def __init__(
        self,
        *,
        type: AutoModActionType,
        metadata: Maybe["AutoModActionMetadata"] = MISSING,
    ) -> None:
        self.type: AutoModActionType = type
        self.metadata: Maybe["AutoModActionMetadata"] = metadata

    @classmethod
    def from_data(cls, data: "AutoModerationActionData") -> Self:
        _type = AutoModActionType(data["type"])
        return cls(
            type=_type,
            metadata=action_metadata_factory(data) if "metadata" in data else MISSING,
        )

    def to_data(self) -> "AutoModerationActionData":
        payload = {
            "type": self.type.value,
        }
        if self.metadata is not MISSING:
            payload["metadata"] = self.metadata.to_data()  # type: ignore
        return payload  # type: ignore


class _BaseActionMetadata:
    @classmethod
    def from_data(cls, data: "AutoModerationActionMetadataData") -> Self:
        return cls(**data)

    def to_data(self) -> "AutoModerationActionMetadataData":
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {''.join([f'{k}={v!r}' for k, v in self.__dict__.items()])}>"


class TimeoutAutoModActionMetadata(_BaseActionMetadata):
    """
    Represents the metadata for an action of type :attr:`.AutoModActionType.TIMEOUT`.

    Attributes
    ----------
    duration: :class:`datetime.timedelta`
        The duration of the timeout.
    """
    __slots__ = ("duration",)

    def __init__(
        self,
        *,
        duration: datetime.timedelta,
    ) -> None:
        self.duration: datetime.timedelta = duration

    def to_data(self) -> "TimeoutAutoModerationActionMetadataData":
        return {
            "duration_seconds": int(self.duration.total_seconds()),
        }


class BlockMessageAutoModActionMetadata(_BaseActionMetadata):
    """
    Represents the metadata for an action of type :attr:`.AutoModActionType.BLOCK_MESSAGE`.

    Attributes
    ----------
    custom_message: :class:`str`
        The custom message to show to the user when their message is blocked.
    """
    __slots__ = ("custom_message",)

    def __init__(
        self,
        *,
        custom_message: str,
    ) -> None:
        self.custom_message: str = custom_message

    def to_data(self) -> "BlockmessageAutoModerationActionMetadataData":
        return {
            "custom_message": self.custom_message,
        }


class SendAlertMessageAutoModActionMetadata(_BaseActionMetadata):
    """
    Represents the metadata for an action of type :attr:`.AutoModActionType.SEND_ALERT_MESSAGE`.

    Attributes
    ----------
    channel_id: :class:`int`
        The ID of the channel to send the alert message to.
    """
    __slots__ = ("channel_id",)

    def __init__(
        self,
        *,
        channel_id: int,
    ) -> None:
        self.channel_id: int = channel_id

    def to_data(self) -> "SendAlertMessageAutoModerationActionMetadataData":
        return {
            "channel_id": self.channel_id,
        }


AutoModActionMetadata = Union[
    TimeoutAutoModActionMetadata,
    BlockMessageAutoModActionMetadata,
    SendAlertMessageAutoModActionMetadata,
]


def action_metadata_factory(data: "AutoModerationActionData") -> AutoModActionMetadata:
    action_type = AutoModActionType(data["type"])
    return {
        AutoModActionType.TIMEOUT: TimeoutAutoModActionMetadata,
        AutoModActionType.BLOCK_MESSAGE: BlockMessageAutoModActionMetadata,
        AutoModActionType.SEND_ALERT_MESSAGE: SendAlertMessageAutoModActionMetadata,
    }[action_type].from_data(data["metadata"])
