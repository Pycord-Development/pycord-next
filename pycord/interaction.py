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

from functools import cached_property
from typing import TYPE_CHECKING

from .embed import Embed
from .errors import InteractionException
from .flags import MessageFlags
from .member import Member
from .message import Message
from .snowflake import Snowflake
from .types import INTERACTION_DATA, Interaction as InteractionData
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .webhook import Webhook

if TYPE_CHECKING:
    from .state import State
    from .ui.text_input import Modal


class InteractionOption:
    def __init__(
        self,
        name: str,
        type: int,
        value: str | int | float | UndefinedType = UNDEFINED,
        options: list[InteractionOption] = [],
        focused: bool | UndefinedType = UNDEFINED,
    ) -> None:
        self.name = name
        self.type = type
        self.value = value
        self.options = options
        self.focused = focused


class Interaction:
    def __init__(
        self, data: InteractionData, state: State, response: bool = False
    ) -> None:
        self._state = state
        if response:
            self.response = InteractionResponse(self)
        self.id = Snowflake(data['id'])
        self.application_id = Snowflake(data['application_id'])
        self.type = data['type']
        self.data: INTERACTION_DATA | UndefinedType = data.get('data', UNDEFINED)
        _guild_id = data.get('guild_id')
        self.guild_id: Snowflake | UndefinedType = (
            Snowflake(_guild_id) if _guild_id is not None else UNDEFINED
        )
        _channel_id = data.get('channel_id')
        self.channel_id: Snowflake | UndefinedType = (
            Snowflake(_channel_id) if _channel_id is not None else UNDEFINED
        )
        _member = data.get('member')
        self.member = Member(_member, state) if _member is not None else UNDEFINED
        _user = data.get('user')
        if self.member is not UNDEFINED:
            self.user = self.member.user
        else:
            self.user = User(_user, state) if _user is not None else UNDEFINED
        self.token = data['token']
        self.version = data['version']
        _message = data.get('message')
        self.message: Message | UndefinedType = (
            Message(_message, state) if _message is not None else UNDEFINED
        )
        self.app_permissions: str | UndefinedType = data.get(
            'app_permissions', UNDEFINED
        )
        self.locale: str | UndefinedType = data.get('locale', UNDEFINED)
        self.guild_locale: str | UndefinedType = data.get('guild_locale', UNDEFINED)
        self.options = []

        # app command data
        if self.type == 2:
            self.command_id = Snowflake(self.data['id'])
            self.name = self.data['name']
            self.application_command_type = self.data['type']
            self.resolved = self.data.get('resolved')
            self.options = [
                InteractionOption(**option) for option in self.data.get('options', [])
            ]
            self.guild_id = (
                Snowflake(data.get('guild_id'))
                if data.get('guild_id') is not None
                else UNDEFINED
            )
        elif self.type == 3:
            self.custom_id = self.data['custom_id']
            self.component_type = self.data['component_type']
            self.values = self.data.get('values', UNDEFINED)

    @property
    def resp(self) -> InteractionResponse:
        return self.response


class InteractionResponse:
    def __init__(self, parent: Interaction) -> None:
        self._parent = parent
        self.responded: bool = False
        self._deferred: bool = False

    @cached_property
    def followup(self) -> Webhook:
        return Webhook(self._parent.id, self._parent.token)

    async def send(
        self,
        content: str,
        tts: bool = False,
        embeds: list[Embed] = [],
        flags: int | MessageFlags = 0,
    ) -> None:
        if self.responded:
            raise InteractionException('This interaction has already been responded to')

        if isinstance(flags, MessageFlags):
            flags = flags.as_bit

        await self._parent._state.http.create_interaction_response(
            self._parent.id,
            self._parent.token,
            {
                'type': 4,
                'data': {
                    'content': content,
                    'tts': tts,
                    'embeds': embeds,
                    'flags': flags,
                },
            },
        )
        self.responded = True

    async def defer(self) -> None:
        if self._deferred:
            raise InteractionException('This interaction has already been deferred')

        await self._parent._state.http.create_interaction_response(
            self._parent.id, self._parent.token, {'type': 5}
        )

        self._deferred = True

    async def send_modal(self, modal: Modal) -> None:
        if self.responded:
            raise InteractionException('This interaction has already been responded to')

        await self._parent._state.http.create_interaction_response(
            self._parent.id, self._parent.token, {'type': 9, 'data': modal._to_dict()}
        )
        self._parent._state.sent_modal(modal)
        self.responded = True
