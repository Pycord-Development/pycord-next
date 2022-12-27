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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .application_commands import ATYPE, ApplicationCommandOptionChoice
from .channel import AllowedMentions, Channel
from .component import Component, SelectOption
from .embed import Embed
from .guild import GuildMember
from .media import Attachment
from .message import Message
from .role import Role
from .snowflake import Snowflake
from .user import LOCALE, User

ITYPE = Literal[
    1,
    2,
    3,
    4,
    5,
]


class ResolvedData(TypedDict):
    users: NotRequired[list[User]]
    members: NotRequired[list[GuildMember]]
    roles: NotRequired[list[Role]]
    channels: NotRequired[list[Channel]]
    messages: NotRequired[list[Message]]
    attachments: NotRequired[list[Attachment]]


class ApplicationCommandInteractionDataOption(TypedDict):
    name: str
    type: ATYPE
    value: NotRequired[str | int | float]
    options: NotRequired[list['ApplicationCommandInteractionDataOption']]
    focused: NotRequired[bool]


class ApplicationCommandData(TypedDict):
    id: Snowflake
    name: str
    type: ATYPE
    resolved: NotRequired[ResolvedData]
    options: NotRequired[list[ApplicationCommandInteractionDataOption]]
    guild_id: NotRequired[Snowflake]
    target_id: NotRequired[Snowflake]


class MessageComponentData(TypedDict):
    custom_id: str
    component_type: int
    values: NotRequired[list[SelectOption]]


class ModalSubmitData(TypedDict):
    custom_id: str
    components: list[Component]


INTERACTION_DATA = (
    ApplicationCommandData
    | ApplicationCommandInteractionDataOption
    | ResolvedData
    | ApplicationCommandData
    | MessageComponentData
    | ModalSubmitData
)


class Interaction(TypedDict):
    id: Snowflake
    application_id: Snowflake
    type: ITYPE
    data: INTERACTION_DATA
    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    member: NotRequired[GuildMember]
    user: NotRequired[User]
    token: str
    version: int
    message: NotRequired[Message]
    app_permissions: str
    locale: LOCALE
    guild_locale: LOCALE


class ICDMessages(TypedDict):
    tts: NotRequired[bool]
    content: NotRequired[str]
    embeds: NotRequired[list[Embed]]
    allowed_mentions: NotRequired[AllowedMentions]
    flags: NotRequired[int]
    components: NotRequired[list[Component]]
    attachments: NotRequired[list[Attachment]]


class ICDAutocomplete(TypedDict):
    choices: list[ApplicationCommandOptionChoice]


class ICDModal(TypedDict):
    custom_id: str
    title: str
    components: list[Component]


ICD = ICDMessages | ICDAutocomplete | ICDModal


class InteractionResponse(TypedDict):
    type: Literal[1, 4, 5, 6, 7, 8, 9]
    data: ICD
