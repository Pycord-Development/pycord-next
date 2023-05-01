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

from typing import TYPE_CHECKING, Any, TypeVar

from aiohttp import BasicAuth

from .api import HTTPClient
from .commands.application import ApplicationCommand
from .events.other import InteractionCreate
from .interaction import Interaction
from .missing import MISSING, Maybe
from .state.core import State
from .types import ApplicationCommand as RawCommand, AsyncFunc
from .user import User
from .utils import compare_application_command, remove_undefined

if TYPE_CHECKING:
    from fastapi import Request, Response

T = TypeVar('T')


class Pycord:
    """HTTP interactions & OAuth implementation."""

    def __init__(
        self,
        token: str,
        synchronize: bool = True,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.__token = token
        self._commands: dict[str, ApplicationCommand] = {}
        self.synchronize_commands = synchronize
        self.http = HTTPClient(token, proxy=proxy, proxy_auth=proxy_auth)
        self.__user = MISSING
        self.__state = State()
        """Fake state used primarily inside classes. Should not be used otherwise."""

        self.__state.http = self.http

    def command(
        self,
        name: Maybe[str] = MISSING,
        cls: T = ApplicationCommand,
        **kwargs: Any,
    ) -> T:
        """
        Create a command.

        Parameters
        ----------
        name: :class:`str`
            The name of the Command.
        cls: type of :class:`.commands.Command`
            The command type to instantiate.
        kwargs: dict[str, Any]
            The kwargs to entail onto the instantiated command.
        """

        def wrapper(func: AsyncFunc) -> T:
            command = cls(func, name=name, state=self.__state, **kwargs)
            self._commands[command.name] = command
            return command

        return wrapper

    async def fastapi(self, request: Request) -> dict[str, Any]:
        # TODO: support modals
        data = await request.json()
        interaction = Interaction(data, self._state, response=True, save=True)

        cmd = self._commands[interaction.name]

        await cmd._invoke(interaction)

        if interaction.response.raw_response:
            return interaction.response.raw_response
        else:
            return {}

    @property
    def user(self) -> User:
        """The most recent version of this bot's user. Should not be used outside of commands."""

        if self.__state.user is None:
            raise AttributeError

        return self.__user

    async def setup(self) -> None:
        self.__state.user = User(await self.http.get_current_user(), self._state)

        global_commands: list[
            RawCommand
        ] = await self.http.get_global_application_commands(self.user.id, True)
        guild_commands: dict[int, list[RawCommand]] = {}

        active_commands: dict[str, ApplicationCommand] = {
            name: command for name, command in self._commands.items()
        }

        # firstly, fetch commands from guilds
        for command in self._commands:
            if command.guild_id is not None and command.guild_id not in guild_commands:
                guild_commands[
                    command.guild_id
                ] = await self.http.get_guild_application_commands(
                    self.user.id, command.guild_id, True
                )

        # now we can synchronize
        for command in global_commands:
            if command['name'] not in active_commands:
                await self.http.delete_global_application_command(
                    self.user.id, command['id']
                )
                continue

            cmd = active_commands[command['name']]

            options = [option.to_dict() for option in cmd.options]

            if options == []:
                options = MISSING

            if not compare_application_command(cmd, command):
                await self.http.edit_global_application_command(
                    self.user.id,
                    command['id'],
                    **remove_undefined(
                        default_member_permissions=cmd.default_member_permissions,
                        name_localizations=cmd.name_localizations,
                        description=cmd.description,
                        description_localizations=cmd.description_localizations,
                        dm_permission=cmd.dm_permission,
                        nsfw=cmd.nsfw,
                        options=options,
                    ),
                )

        for command in guild_commands:
            if command['name'] not in active_commands:
                await self.http.delete_guild_application_command(
                    self.user.id, command['guild_id'], command['id']
                )
                continue

            cmd = active_commands[command['name']]

            options = [option.to_dict() for option in cmd.options]

            if options == []:
                options = MISSING

            if not compare_application_command(cmd, command):
                await self.http.edit_guild_application_command(
                    self.user.id,
                    command['id'],
                    command['guild_id'],
                    **remove_undefined(
                        default_member_permissions=cmd.default_member_permissions,
                        name_localizations=cmd.name_localizations,
                        description=cmd.description,
                        description_localizations=cmd.description_localizations,
                        dm_permission=cmd.dm_permission,
                        nsfw=cmd.nsfw,
                        options=options,
                    ),
                )
