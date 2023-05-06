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

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Callable, Generic, Type, TypeVar

from ...commands import Command, Group
from ...commands.application.command import ApplicationCommand
from ...events.event_manager import Event
from ...missing import MISSING, MissingEnum
from ...types import AsyncFunc

if TYPE_CHECKING:
    from ...bot import Bot


T = TypeVar('T')
AF = TypeVar('AF')


class BaseContext(SimpleNamespace):
    ...


ContextT = TypeVar('ContextT', bound=BaseContext)


class Gear(Generic[ContextT]):
    """
    The Gear. A set of commands & events separate from Bot.
    Useful for multi-file separation for huge bots.

    Parameters
    ----------
    name: :class:`str`
        The name of this Gear.

    Attributes
    ----------
    bot: Union[:class:`pycord.Bot`, None]
        The bot this Gear is attached to.
    """

    ctx: ContextT

    __slots__ = ('_listener_functions', '_commands', 'name', 'ctx', 'bot')

    def __init__(self, name: str, ctx: ContextT | None = None) -> None:
        self.name = name
        self._listener_functions: dict[Type[Event], list[AsyncFunc]] = {}
        self.bot: Bot
        self._commands: list[Command | Group] = []
        if ctx is None:
            self.ctx = BaseContext()
        else:
            self.ctx = ctx

    async def on_attach(self, *args, **kwargs) -> None:
        ...

    def listen(self, name: str) -> T:
        """
        Listen to an event

        Parameters
        ----------
        name: :class:`str`
            The name of the event to listen to.
        """

        def wrapper(func: T) -> T:
            if self._listener_functions.get(name):
                self._listener_functions[name].append(func)
            else:
                self._listener_functions[name] = [func]
            return func

        return wrapper

    def command(
        self,
        name: str | MissingEnum = MISSING,
        cls: Type[T] = ApplicationCommand,
        **kwargs: Any,
    ) -> T:
        """
        Create a command within the Gear

        Parameters
        ----------
        name: :class:`str`
            The name of the Command.
        cls: type of :class:`.commands.Command`
            The command type to instantiate.
        kwargs: dict[str, Any]
            The kwargs to entail onto the instantiated command.
        """

        def wrapper(func: AsyncFunc) -> Command:
            command = cls(func, state=None, name=name, **kwargs)
            self._commands.append(command)
            return command

        return wrapper

    def group(self, name: str, cls: Type[Group], **kwargs: Any) -> Callable[[AF], AF]:
        """
        Create a brand-new Group of Commands

        Parameters
        ----------
        name: :class:`str`
            The name of the Group.
        cls: type of :class:`.commands.Group`
            The group type to instantiate.
        kwargs: dict[str, Any]
            The kwargs to entail onto the instantiated group.
        """

        def wrapper(func: AF) -> AF:
            # I know this partially ruins typing, but
            # Gears are loaded before events are taken in, so
            # theoretically nothing can break with state being None.
            r = cls(func, name, None, **kwargs)  # type: ignore
            self._commands.append(r)
            return r

        return wrapper

    def attach(self, bot: Bot) -> None:
        """
        Attaches this Gear to a bot.

        Parameters
        ----------

        bot: :class:`pycord.Bot`
            The bot to attach onto
        """

        for name, funcs in self._listener_functions.items():
            for func in funcs:
                bot._state.event_manager.add_event(name, func)

        for cmd in self._commands:
            if isinstance(cmd, Command):
                cmd._state = bot._state
                cmd._state.commands.append(cmd)
            elif isinstance(cmd, Group):
                cmd._state = bot._state

        self.bot = bot

        self.bot._state.gears.append(self)
