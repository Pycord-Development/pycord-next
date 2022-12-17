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
from ...types.interaction import ApplicationCommandData
from ...undefined import UNDEFINED, UndefinedType
from ...interaction import Interaction
from ..command import Command
from typing import Coroutine
from ..group import Group
from ...state import State
from dataclasses import dataclass
from ...snowflake import Snowflake

__all__ = ['CommandChoice', 'ApplicationCommandOption', 'ApplicationCommand']

@dataclass
class CommandChoice:
    name: str
    value: str | int | float
    name_localizations: dict[str, str] | None = None

class ApplicationCommandOption:
    def __init__(
        self,
        name: str,
        name_localizations: dict[str, str] | None = None,
        description: str | None = None,
        description_localizations: dict[str, str] | None = None,
        required: bool = False,
        choices: list[CommandChoice] | None = None,
        options: list["ApplicationCommandOption"] = [],
        channel_types: list[int] | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
        autocomplete: bool | None = None
    ) -> None:
        self.name = name
        self.name_localizations = name_localizations
        self.description = description
        self.description_localizations = description_localizations
        self.required = required
        self.choices = choices
        self.options = options
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete
        

class ApplicationCommand(Command):
    _processor_event = 'on_interaction'
    sub_level: int = 0

    def __init__(
        self,
        # normal parameters
        callback: Coroutine,
        name: str,
        type: int,
        description: str,
        state: State,
        guild_id: int | None = None,
        group: Group | None = None,
        # discord parameters
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        dm_permission: bool = True,
        nsfw: bool = False,
    ) -> None:
        super().__init__(callback, name, state, group)

        self.type = type
        self.guild_id = guild_id
        self.name_localizations = name_localizations
        self.description = description
        self.description_localizations = description_localizations
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self._subs: list[ApplicationCommand] = []
        self._created: bool = False

    async def instantiate(self) -> None:
        if self.guild_id:
            guild_commands: list[ApplicationCommandData] = await self._state.http.get_guild_application_commands(self._state.user.id, self.guild_id, True)

            for app_cmd in guild_commands:
                if app_cmd['name'] == self.name:
                    await self._state.http.edit_guild_application_command(
                        self._state.user.id,
                        Snowflake(app_cmd['id']),
                        guild_id=self.guild_id,
                        name=self.name,
                        name_localizations=self.name_localizations,
                        description=self.description,
                        description_localizations=self.description_localizations,
                        type=self.type
                    )
                    self._created = True
                    break

            if not self._created:
                await self._state.http.create_guild_application_command(
                    self._state.user.id,
                    guild_id=self.guild_id,
                    name=self.name,
                    name_localizations=self.name_localizations,
                    description=self.description,
                    description_localizations=self.description_localizations,
                    type=self.type
                )

            return

        for app_cmd in self._state.application_commands:
            if app_cmd['name'] == self.name:
                await self._state.http.edit_global_application_command(
                    self._state.user.id,
                    Snowflake(app_cmd['id']),
                    name=self.name,
                    name_localizations=self.name_localizations,
                    description=self.description,
                    description_localizations=self.description_localizations,
                    type=self.type
                )
                self._created = True

        if not self._created:
            await self._state.http.create_global_application_command(
                self._state.user.id,
                name=self.name,
                name_localizations=self.name_localizations,
                description=self.description,
                description_localizations=self.description_localizations,
                type=self.type
            )

    async def _invoke(self, interaction: Interaction) -> None:
        if interaction.data:
            if interaction.data.get('name') is not None:
                if interaction.data['name'] == self.name:
                    await self._callback(interaction)
