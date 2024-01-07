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


from curses import meta
import datetime
from .enums import AutoModEventType, AutoModTriggerType, AutoModActionType, AutoModKeywordPresetType
from .mixins import Identifiable
from .missing import Maybe, MISSING

from typing import TYPE_CHECKING, Self, Union

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
    __slots__ = (
        "id",
        "guild_id",
        "name",
        "creator_id",
        "event_type",
        "trigger_type",
        "trigger_metadata",
        "actions",
        "enabled",
        "exempt_roles",
        "exempt_channels",
    )
    def __init__(self, data: "AutoModerationRuleData", state: "State") -> None:
        self.id: int = int(data["id"])
        self.guild_id: int = int(data["guild_id"])
        self.name: str = data["name"]
        self.creator_id: int = int(data["creator_id"])
        self.event_type: AutoModEventType = AutoModEventType(data["event_type"])
        self.trigger_type: AutoModTriggerType = AutoModTriggerType(data["trigger_type"])
        self.trigger_metadata: Maybe[AutoModTriggerMetadata] = trigger_metadata_factory(data)
        self.actions: list[AutoModAction] = [AutoModAction.from_data(x) for x in data["actions"]]
        self.enabled: bool = data["enabled"]
        self.exempt_roles: list[int] = [int(x) for x in data["exempt_roles"]]
        self.exempt_channels: list[int] = [int(x) for x in data["exempt_channels"]]

    def __repr__(self) -> str:
        return f"<AutoModRule id={self.id} name={self.name!r} event_type={self.event_type} trigger_type={self.trigger_type} creator_id={self.creator_id} enabled={self.enabled}>"
    
    def __str__(self) -> str:
        return self.name
    
    async def modify(self, **kwargs) -> "AutoModRule":
        raise NotImplementedError  # TODO
    
    async def delete(self, *, reason: Maybe[str]) -> None:
        raise NotImplementedError  # TODO


class _BaseTriggerMetadata:
    @classmethod
    def from_data(cls, data: "AutoModerationTriggerMetadataData") -> Self:
        return cls(**data)
    
    def to_data(self) -> "AutoModerationTriggerMetadataData":
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {''.join([f'{k}={v!r}' for k, v in self.__dict__.items()])}>"


class KeywordAutoModTriggerMetadata(_BaseTriggerMetadata):
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

    def to_data(self) -> "KeywordAutoModerationTriggerMetadataData":
        return {
            "keyword_filter": self.keyword_filter,
            "regex_patterns": self.regex_patterns,
            "allow_list": self.allow_list,
        }

    
class KeywordPresetAutoModTriggerMetadata(_BaseTriggerMetadata):
    __slots__ = ("presets", "allow_list")
    def __init__(
            self,
            *,
            presets: list[AutoModKeywordPresetType],
            allow_list: list[str],
    ) -> None:
        self.presets: list[AutoModKeywordPresetType] = presets
        self.allow_list: list[str] = allow_list

    def to_data(self) -> "KeywordPresetAutoModerationTriggerMetadataData":
        return {
            "presets": [x.value for x in self.presets],
            "allow_list": self.allow_list,
        }


class MentionSpamAutoModTriggerMetadata(_BaseTriggerMetadata):
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
