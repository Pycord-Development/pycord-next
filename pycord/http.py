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
from .errors import PycordException
from .interaction import Interaction
from .missing import MISSING, Maybe
from .state.core import State
from .types import ApplicationCommand as RawCommand, AsyncFunc
from .user import User
from .utils import compare_application_command, remove_undefined

try:
    from nacl.exceptions import BadSignatureError
    from nacl.signing import VerifyKey

    has_nacl = True
except ImportError:
    has_nacl = False

if TYPE_CHECKING:
    from fastapi import Request

T = TypeVar('T')


class DiscordException(PycordException):
    ...


class Pycord:
    """HTTP interactions & OAuth implementation."""

    def __init__(
        self,
        token: str,
        public_key: str,
        synchronize: bool = True,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        if not has_nacl:
            raise RuntimeError('PyNaCl must be installed to use HTTP Interactions.')

        self.__token = token
        self._commands: dict[str, ApplicationCommand] = {}
        self.synchronize_commands = synchronize
        self.public_key = public_key
        self.verify_key = VerifyKey(bytes.fromhex(self.public_key))
        self.http = HTTPClient(token, proxy=proxy, proxy_auth=proxy_auth)
        self.__state = State()
        """Fake state used primarily inside classes. Should not be used otherwise."""

        self.__state.http = self.http

    def verify_signature(self, sig: str, ts: str, body: str) -> None:
        try:
            self.verify_key.verify(f'{ts}{body}'.encode(), bytes.fromhex(sig))
        except BadSignatureError:
            raise DiscordException('Invalid request signature')

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
        self.verify_signature(
            request.headers.get('X-Signature-Ed25519', ''),
            request.headers.get('X-Signature-Timestamp', ''),
            (await request.body()).decode('utf-8'),
        )

        data = await request.json()
        type = data['type']
        name = data['data']['name']

        if type == 1:
            return {'type': 1}

        cmd = self._commands[name]

        proc: Interaction = cmd._processor_event._interaction_object(
            data, self.__state, response=True, save=True
        )

        await cmd._invoke(proc)

        return proc.response.raw_response or {}

    @property
    def user(self) -> User:
        """The most recent version of this bot's user. Should not be used outside of commands."""

        if self.__state.user is None:
            raise AttributeError

        return self.__state.user

    async def setup(self) -> None:
        self.__state.user = User(await self.http.get_current_user(), self.__state)

        if not self.synchronize_commands:
            return

        global_commands: list[
            RawCommand
        ] = await self.http.get_global_application_commands(self.user.id, True)
        guild_commands: dict[int, list[RawCommand]] = {}
        global_command_names = [c['name'] for c in global_commands]
        guild_command_names: dict[int, list[str]] = {
            gid: [cmd['name'] for cmd in cmds] for gid, cmds in guild_commands.items()
        }

        active_commands: dict[str, ApplicationCommand] = {
            name: command for name, command in self._commands.items()
        }

        # firstly, fetch commands from guilds
        for command in self._commands.values():
            if (
                command.guild_id is not None
                and command.guild_id not in guild_commands.values()
            ):
                guild_commands[
                    command.guild_id
                ] = await self.http.get_guild_application_commands(
                    self.user.id, command.guild_id, True
                )

        for command in self._commands.values():
            if not command.guild_id and command.name not in global_command_names:
                cmd = await self.http.create_global_application_command(
                    self.user.id,
                    name=command.name,
                    name_localizations=command.name_localizations,
                    description=command.description,
                    description_localizations=command.description_localizations,
                    options=[option.to_dict() for option in command.options],
                    default_member_permissions=command.default_member_permissions,
                    dm_permission=command.dm_permission,
                    type=command.type,
                )
                command.id = int(cmd['id'])
            elif command.guild_id and command.name not in guild_command_names.get(
                command.guild_id, []
            ):
                cmd = await self.http.create_guild_application_command(
                    self.user.id,
                    command.guild_id,
                    name=command.name,
                    name_localizations=command.name_localizations,
                    description=command.description,
                    description_localizations=command.description_localizations,
                    options=[option.to_dict() for option in command.options],
                    default_member_permissions=command.default_member_permissions,
                    dm_permission=command.dm_permission,
                    type=command.type,
                )
                command.id = int(cmd['id'])
            elif command.guild_id:
                for cmd in guild_commands[command.guild_id]:
                    if cmd['name'] == command.name:
                        command.id = int(cmd['id'])
                        break
                else:
                    raise RuntimeError()

                options = [option.to_dict() for option in command.options]

                if options == []:
                    options = MISSING

                if not compare_application_command(command, cmd):
                    await self.http.edit_guild_application_command(
                        self.user.id,
                        command.id,
                        command.guild_id,
                        **remove_undefined(
                            default_member_permissions=command.default_member_permissions,
                            name_localizations=command.name_localizations,
                            description=command.description,
                            description_localizations=cmd.description_localizations,
                            dm_permission=command.dm_permission,
                            nsfw=command.nsfw,
                            options=options,
                        ),
                    )
            elif not command.guild_id:
                for cmd in global_commands:
                    if cmd['name'] == command.name:
                        command.id = int(cmd['id'])
                        break
                else:
                    raise RuntimeError()

                options = [option.to_dict() for option in command.options]

                if options == []:
                    options = MISSING

                if not compare_application_command(command, cmd):
                    await self.http.edit_global_application_command(
                        self.user.id,
                        command.id,
                        **remove_undefined(
                            default_member_permissions=command.default_member_permissions,
                            name_localizations=command.name_localizations,
                            description=command.description,
                            description_localizations=cmd.description_localizations,
                            dm_permission=command.dm_permission,
                            nsfw=command.nsfw,
                            options=options,
                        ),
                    )

        # now we can synchronize
        for command in global_commands:
            if command['name'] not in active_commands:
                await self.http.delete_global_application_command(
                    self.user.id, command['id']
                )
                continue

        for commands in guild_commands.values():
            for command in commands:
                if command['name'] not in active_commands:
                    await self.http.delete_guild_application_command(
                        self.user.id, command['guild_id'], command['id']
                    )
                    continue
