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

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Coroutine

from ...enums import ApplicationCommandOptionType
from ...snowflake import Snowflake
from ...types.interaction import ApplicationCommandData
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined
from ..command import Command
from ..group import Group

if TYPE_CHECKING:
    from ...interaction import Interaction
    from ...state import State

__all__ = ['CommandChoice', 'Option', 'ApplicationCommand']


@dataclass
class CommandChoice:
    name: str
    value: str | int | float
    name_localizations: dict[str, str] | None = None


class Option:
    def __init__(
        self,
        type: ApplicationCommandOptionType,
        name: str,
        description: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        required: bool | UndefinedType = UNDEFINED,
        choices: list[CommandChoice] | UndefinedType = UNDEFINED,
        options: list['Option'] | UndefinedType = UNDEFINED,
        channel_types: list[int] | UndefinedType = UNDEFINED,
        min_value: int | UndefinedType = UNDEFINED,
        max_value: int | UndefinedType = UNDEFINED,
        autocomplete: bool | UndefinedType = UNDEFINED,
    ) -> None:
        self.type = type.value
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

    def to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            type=self.type,
            name=self.name,
            name_localizations=self.name_localizations,
            description=self.description,
            description_localizations=self.description_localizations,
            required=self.required,
            choices=self.choices,
            options=[option.to_dict() for option in self.options]
            if self.options is not UNDEFINED
            else UNDEFINED,
            channel_types=self.channel_types,
            min_value=self.min_value,
            max_value=self.max_value,
            autocomplete=self.autocomplete,
        )


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
        options: list[Option] | UndefinedType = UNDEFINED,
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
        self.options = options
        if options is not UNDEFINED:
            self._options = []
            for option in options:
                self._options.append(option.to_dict())

    async def instantiate(self) -> None:
        if self.guild_id:
            guild_commands: list[
                ApplicationCommandData
            ] = await self._state.http.get_guild_application_commands(
                self._state.user.id, self.guild_id, True
            )

            for app_cmd in guild_commands:
                if app_cmd['name'] == self.name and self._state.update_commands:
                    await self._state.http.edit_guild_application_command(
                        self._state.user.id,
                        Snowflake(app_cmd['id']),
                        guild_id=self.guild_id,
                        name=self.name,
                        name_localizations=self.name_localizations,
                        description=self.description,
                        description_localizations=self.description_localizations,
                        type=self.type,
                        options=self._options,
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
                    type=self.type,
                    options=self._options,
                )

            return

        for app_cmd in self._state.application_commands:
            if app_cmd['name'] == self.name and self._state.update_commands:
                await self._state.http.edit_global_application_command(
                    self._state.user.id,
                    Snowflake(app_cmd['id']),
                    name=self.name,
                    name_localizations=self.name_localizations,
                    description=self.description,
                    description_localizations=self.description_localizations,
                    type=self.type,
                    options=self._options,
                )
                self._created = True
                break

        if not self._created:
            await self._state.http.create_global_application_command(
                self._state.user.id,
                name=self.name,
                name_localizations=self.name_localizations,
                description=self.description,
                description_localizations=self.description_localizations,
                type=self.type,
                options=self._options,
            )

    async def _invoke(self, interaction: Interaction) -> None:
        if interaction.data:
            if interaction.data.get('name') is not None:
                if interaction.data['name'] == self.name:
                    await self._callback(interaction, *interaction.options)
