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
from .missing import MISSING, Maybe, MissingEnum
from .snowflake import Snowflake
from .types import INTERACTION_DATA, Interaction as InteractionData
from .user import User
from .webhook import Webhook

if TYPE_CHECKING:
    from .state import State
    from .ui.text_input import Modal


class InteractionOption:
    __slots__ = ('name', 'type', 'value', 'options', 'focused')

    def __init__(
        self,
        name: str,
        type: int,
        value: str | int | float | MissingEnum = MISSING,
        options: list[InteractionOption] = [],
        focused: bool | MissingEnum = MISSING,
    ) -> None:
        self.name = name
        self.type = type
        self.value = value
        self.options = options
        self.focused = focused


class Interaction:
    __slots__ = (
        '_state',
        'response',
        'id',
        'application_id',
        'type',
        'data',
        'guild_id',
        'channel_id',
        'member',
        'user',
        'token',
        'version',
        'message',
        'app_permissions',
        'locale',
        'guild_locale',
        'options',
        'command_id',
        'name',
        'application_command_type',
        'resolved',
        'options',
        'guild_id',
        'custom_id',
        'component_type',
        'values',
    )

    def __init__(
        self,
        data: InteractionData,
        state: State,
        response: bool = False,
        save: bool = False,
    ) -> None:
        self._state = state
        if response:
            self.response = InteractionResponse(self, save=save)
        self.id = Snowflake(data['id'])
        self.application_id = Snowflake(data['application_id'])
        self.type = data['type']
        self.data: INTERACTION_DATA | MissingEnum = data.get('data', MISSING)
        _guild_id = data.get('guild_id')
        self.guild_id: Snowflake | MissingEnum = (
            Snowflake(_guild_id) if _guild_id is not None else MISSING
        )
        _channel_id = data.get('channel_id')
        self.channel_id: Snowflake | MissingEnum = (
            Snowflake(_channel_id) if _channel_id is not None else MISSING
        )
        _member = data.get('member')
        self.member = (
            Member(_member, state, guild_id=self.guild_id)
            if _member is not None
            else MISSING
        )
        _user = data.get('user')
        if self.member is not MISSING:
            self.user = self.member.user
        else:
            self.user = User(_user, state) if _user is not None else MISSING
        self.token = data['token']
        self.version = data['version']
        _message = data.get('message')
        self.message: Message | MissingEnum = (
            Message(_message, state) if _message is not None else MISSING
        )
        self.app_permissions: str | MissingEnum = data.get('app_permissions', MISSING)
        self.locale: str | MissingEnum = data.get('locale', MISSING)
        self.guild_locale: str | MissingEnum = data.get('guild_locale', MISSING)
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
                else MISSING
            )
        elif self.type == 3:
            self.custom_id = self.data['custom_id']
            self.component_type = self.data['component_type']
            self.values = self.data.get('values', MISSING)

    @property
    def resp(self) -> InteractionResponse:
        return self.response


class InteractionResponse:
    __slots__ = ('_parent', '_deferred', 'responded')

    def __init__(self, parent: Interaction, save: bool) -> None:
        self._parent = parent
        self.responded: bool = False
        self._deferred: bool = False
        self._save = save
        self.raw_response = None

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

        if self.save:
            self.raw_response = {
                'type': 4,
                'data': {
                    'content': content,
                    'tts': tts,
                    'embeds': embeds,
                    'flags': flags,
                },
            }
            self.responded = True
            return

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
        if self._deferred or self.responded:
            raise InteractionException(
                'This interaction has already been deferred or responded to'
            )

        await self._parent._state.http.create_interaction_response(
            self._parent.id, self._parent.token, {'type': 5}
        )

        self._deferred = True
        self.responded = True

    async def send_modal(self, modal: Modal) -> None:
        if self.responded:
            raise InteractionException('This interaction has already been responded to')

        await self._parent._state.http.create_interaction_response(
            self._parent.id, self._parent.token, {'type': 9, 'data': modal._to_dict()}
        )
        self._parent._state.sent_modal(modal)
        self.responded = True

    async def autocomplete(self, choices: list[str]) -> None:
        if self.responded:
            raise InteractionException('This interaction has already been responded to')

        if self._save:
            self.raw_response = {
                'type': 8,
                'data': {'choices': choices},
            }

        await self._state.http.create_interaction_response(
            self._parent.id,
            self._parent.token,
            {
                'type': 8,
                'data': {'choices': choices},
            },
        )
