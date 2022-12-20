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

import asyncio
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Coroutine

from ...channel import identify_channel
from ...enums import ApplicationCommandOptionType, ApplicationCommandType
from ...interaction import Interaction, InteractionOption
from ...media import Attachment
from ...member import Member
from ...role import Role
from ...snowflake import Snowflake
from ...types.interaction import ApplicationCommandData
from ...undefined import UNDEFINED, UndefinedType
from ...user import User
from ...utils import remove_undefined
from ..command import Command
from ..group import Group
from .arguments import ArgumentParser
from .errors import ApplicationCommandException

if TYPE_CHECKING:
    from ...state import State

__all__ = ['CommandChoice', 'Option', 'ApplicationCommand']

arg_parser = ArgumentParser()


@dataclass
class CommandChoice:
    name: str
    value: str | int | float
    name_localizations: dict[str, str] | None = None


class Option:
    _level: int = 0

    def __init__(
        self,
        type: ApplicationCommandOptionType | int,
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
        if isinstance(type, ApplicationCommandOptionType):
            self.type = type.value
        else:
            self.type = type
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
        self._subs = {}

        if TYPE_CHECKING:
            self.focused: bool | UndefinedType = UNDEFINED
            self.value: str | int | float | UndefinedType = UNDEFINED
            self.options: list[InteractionOption] = UNDEFINED
            self._param: str = UNDEFINED
            self._callback: Coroutine | None = UNDEFINED

    @property
    def callback(self) -> Coroutine:
        return self._callback

    @callback.setter
    def callback(self, call: Coroutine) -> None:
        arg_defaults = arg_parser.get_arg_defaults(self._callback)
        self.options: list[Option] = []
        self._options_dict: dict[str, Option] = {}

        i: int = 0

        for name, v in arg_defaults.items():
            # ignore interaction
            if i == 0:
                i += 1
                continue

            if v[0] is None and name != 'self':
                raise ApplicationCommandException(
                    f'Parameter {name} on command {self.name} has no default set'
                )
            elif name == 'self':
                continue
            elif not isinstance(v[0], Option):
                raise ApplicationCommandException(
                    f'Options may only be of type Option, not {v[0]}'
                )

            v[0]._param = name

            self.options.append(v[0])
            self._options_dict[v[0].name] = v[0]

        self._options = []

        for option in self.options:
            self._options.append(option.to_dict())

    def __get__(self):
        return self.value

    def _inter_copy(self, data: InteractionOption) -> Option:
        c = copy(self)

        c.focused = data.focused
        c.value = data.value
        c.options = data.options
        return c

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

    def command(
        self,
        name: str,
        description: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
    ) -> ApplicationCommand:
        def wrapper(func: Coroutine):
            command = Option(
                type=1,
                name=name,
                description=description,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
            command._callback = func
            command._level = self._level + 1

            if self._subs == {}:
                self.options = []
                self._callback = None

            self.options.append(command)

            self._subs[name] = command

            if self.type == 1:
                # turn into a command group
                self.type = 2

            return command

        return wrapper


class ApplicationCommand(Command):
    _processor_event = 'on_interaction'
    sub_level: int = 0

    def __init__(
        self,
        # normal parameters
        callback: Coroutine | None,
        name: str,
        type: int | ApplicationCommandType,
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

        if isinstance(type, ApplicationCommandType):
            self.type = type.value
        else:
            self.type = type

        self.guild_id = guild_id
        self.name_localizations = name_localizations
        self.description = description
        self.description_localizations = description_localizations
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        if self.type == 1:
            self._subs: dict[str, ApplicationCommand] = {}
            self._parse_arguments()
        self._created: bool = False

    def command(
        self,
        name: str,
        description: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
    ) -> ApplicationCommand:
        def wrapper(func: Coroutine):
            command = Option(
                type=1,
                name=name,
                description=description,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )
            command._callback = func
            command._level = 1

            if self._subs == {}:
                self.options = []
                self._options_dict = {}
                self._options = []
                self._callback = None

            self.options.append(command)
            self._options_dict[name] = command
            self._options.append(command.to_dict())

            self._subs[name] = command
            return command

        return wrapper

    def _parse_arguments(self) -> None:
        arg_defaults = self._state.arg_parser.get_arg_defaults(self._callback)
        self.options: list[Option] = []
        self._options_dict: dict[str, Option] = {}

        i: int = 0

        for name, v in arg_defaults.items():
            # ignore interaction
            if i == 0:
                i += 1
                continue

            if v[0] is None and name != 'self':
                raise ApplicationCommandException(
                    f'Parameter {name} on command {self.name} has no default set'
                )
            elif name == 'self':
                continue
            elif not isinstance(v[0], Option):
                raise ApplicationCommandException(
                    f'Options may only be of type Option, not {v[0]}'
                )

            v[0]._param = name

            self.options.append(v[0])
            self._options_dict[v[0].name] = v[0]

        self._options = []

        for option in self.options:
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

    def _process_options(
        self, interaction: Interaction, options: list[InteractionOption]
    ) -> dict[str, Any]:
        binding = {}
        for option in options:
            o = self._options_dict[option.name]
            if option.type == 1:
                sub = self._subs[option.name]

                opts = self._process_options(
                    interaction=interaction, options=option.options
                )
                asyncio.create_task(sub._callback(interaction, **opts))
            elif option.type == 2:
                self._process_options(interaction=interaction, options=option.options)
            elif option.type in (3, 4, 5, 10):
                binding[o._param] = o._inter_copy(option)
            elif option.type == 6:
                user = User(
                    interaction.data['resolved']['users'][option.value], self._state
                )

                if interaction.guild_id:
                    member = Member(
                        interaction.data['resolved']['members'][option.value],
                        self._state,
                    )
                    member.user = user

                    binding[o._param] = member
                else:
                    binding[o._param] = user
            elif option.type == 7:
                binding[o._param] = identify_channel(
                    interaction.data['resolved']['channels'][option.value], self._state
                )
            elif option.type == 8:
                binding[o._param] = Role(
                    interaction.data['resolved']['roles'][option.value], self._state
                )
            elif option.type == 9:
                if interaction.data['resolved'].get('roles'):
                    binding[o._param] = Role(
                        interaction.data['resolved']['roles'][option.value], self._state
                    )
                else:
                    user = User(
                        interaction.data['resolved']['users'][option.value], self._state
                    )

                    if interaction.guild_id:
                        member = Member(
                            interaction.data['resolved']['members'][option.value],
                            self._state,
                        )
                        member.user = user

                        binding[o._param] = member
                    else:
                        binding[o._param] = user
            elif option.type == 11:
                binding[o._param] = Attachment(
                    interaction.data['resolved']['attachments'][option.value],
                    self._state,
                )

        return binding

    async def _invoke(self, interaction: Interaction) -> None:
        if interaction.data:
            if interaction.data.get('name') is not None:
                if interaction.data['type'] != self.type:
                    return

                if interaction.data['name'] == self.name:
                    if interaction.data['type'] == 1:
                        binding = self._process_options(
                            interaction, interaction.options
                        )

                        if self._callback:
                            await self._callback(interaction, **binding)
                    elif interaction.data['type'] == 2:
                        ...
