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
from typing import TYPE_CHECKING, Any

from ..user import User
from .event_manager import Event

if TYPE_CHECKING:
    from ..state import State


class Ready(Event):
    _name = 'READY'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        user = User(data['user'], state)
        state.user = user
        self.user = user

        if hasattr(state, '_raw_user_fut'):
            state._raw_user_fut.set_result(None)

        state._ready = True

        for gear in state.gears:
            asyncio.create_task(gear.on_attach(), name=f'Attaching Gear: {gear.name}')

        state._available_guilds: list[int] = [uag['id'] for uag in data['guilds']]

        state.application_commands = []
        state.application_commands.extend(
            await state.http.get_global_application_commands(state.user.id, True)
        )
        state._application_command_names: list[str] = []

        for command in state.commands:
            await command.instantiate()
            if hasattr(command, 'name'):
                state._application_command_names.append(command.name)

        for app_command in state.application_commands:
            if app_command['name'] not in state._application_command_names:
                await state.http.delete_global_application_command(
                    state.user.id.real, app_command['id']
                )

        return True