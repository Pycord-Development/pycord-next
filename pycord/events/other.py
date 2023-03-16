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


import asyncio
from typing import TYPE_CHECKING, Any, Type

from ..interaction import Interaction
from ..message import Message
from ..user import User
from .event_manager import Event

if TYPE_CHECKING:
    from ..state import State


class Ready(Event):
    _name = 'READY'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        state._available_guilds: list[int] = [int(uag['id']) for uag in data['guilds']]

        user = User(data['user'], state)
        state.user = user
        self.user = user

        if not state._ready:
            if hasattr(state, '_raw_user_fut'):
                state._raw_user_fut.set_result(None)

            state._ready = True

            for gear in state.gears:
                asyncio.create_task(
                    gear.on_attach(), name=f'Attaching Gear: {gear.name}'
                )

            state.application_commands = []
            state.application_commands.extend(
                await state.http.get_global_application_commands(state.user.id, True)
            )
            state._application_command_names: list[str] = []

            for command in state.commands:
                await command.instantiate()
                state.event_manager.add_event(command._processor_event, command._invoke)
                if hasattr(command, 'name'):
                    state._application_command_names.append(command.name)

            for app_command in state.application_commands:
                if app_command['name'] not in state._application_command_names:
                    await state.http.delete_global_application_command(
                        state.user.id.real, app_command['id']
                    )


class Hook(Event):
    _name = 'READY'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        if state._ready is True:
            return False

        user = User(data['user'], state)
        self.user = user


class UserUpdate(Event):
    _name = 'USER_UPDATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        self.user = User(data, state)
        state.user = self.user
        state.raw_user = data


class InteractionCreate(Event):
    _name = 'INTERACTION_CREATE'

    def __init__(self, interaction: Type[Interaction] = Interaction) -> None:
        self.__interaction_object = interaction

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        interaction = self.__interaction_object(data, state, True)

        self.interaction = interaction


class InteractionInvoke(Event):
    _name = 'INTERACTION_CREATE'

    def __init__(
        self, custom_id: str, interaction: Type[Interaction] = Interaction
    ) -> None:
        self.__interaction_object = interaction
        self.__custom_id = custom_id

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        interaction = self.__interaction_object(data, state, True)

        self.interaction = interaction

        if self.__custom_id != interaction.custom_id:
            return False


class WaitForMessage(Event):
    _name = 'MESSAGE_CREATE'

    def __init__(
        self, user_id: int | None = None, channel_id: int | None = None
    ) -> None:
        self.__user_id = user_id
        self.__channel_id = channel_id

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        message = Message(data, state)
        self.message = message
        self.is_human = message.author.bot is False
        self.content = self.message.content

        await (state.store.sift('messages')).save(
            [message.channel_id], message.id, message
        )

        if self.__user_id and self.__channel_id:
            if (
                self.__user_id != message.author.id
                or self.__channel_id != message.channel_id
            ):
                return False

        elif self.__user_id:
            if self.__user_id != message.author.id:
                return False

        elif self.__channel_id:
            if self.__channel_id != message.channel_id:
                return False
