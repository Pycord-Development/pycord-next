# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
# Copyright (c) 2022-present Pycord Development
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

from typing import TYPE_CHECKING, Any, Callable, Coroutine, Type, TypeVar

from ...commands import Command, Group

if TYPE_CHECKING:
    from ...bot import Bot

T = TypeVar('T')
CoroFunc = Callable[..., Coroutine[Any, Any, Any]]
CoroFuncT = TypeVar('CoroFuncT', bound=Callable[..., Any])
CommandT = TypeVar('CommandT', bound=Command)
GroupT = TypeVar('GroupT', bound=Group)


class Gear:
    """
    The Gear. Pycord's reinterpretation of Cogs in a way which is easier for both developers and library developers.
    It removes the old subclass-based system with a new instance-based system.

    Parameters
    ----------
    name: :class:`str`
        The name of this Gear.

    Attributes
    ----------
    bot: Union[:class:`pycord.Bot`, None]
        The bot this Gear is attached to.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._listener_functions: dict[str, list[CoroFunc]] = {}
        self.bot: Bot
        self._commands: list[Command | Group] = []

    async def on_attach(self, *args, **kwargs) -> None:
        ...

    def listen(self, name: str) -> Callable[[CoroFuncT], CoroFuncT]:
        def wrapper(func: CoroFuncT) -> CoroFuncT:
            if self._listener_functions.get(name):
                self._listener_functions[name].append(func)
            else:
                self._listener_functions[name] = [func]
            return func

        return wrapper

    def command(self, name: str, cls: Type[CommandT], **kwargs: Any) -> Callable[[CoroFunc], CommandT]:
        def wrapper(func: CoroFunc) -> CommandT:
            # no idea why state is None here
            command = cls(func, name, None, **kwargs)  # pyright: ignore
            self._commands.append(command)
            return command

        return wrapper

    def group(self, name: str, cls: Type[GroupT], **kwargs: Any) -> Callable[[CoroFunc], GroupT]:
        def wrapper(func: CoroFunc) -> GroupT:
            # see above
            r = cls(func, name, None, **kwargs)  # pyright: ignore
            self._commands.append(r)
            return r

        return wrapper

    def attach(self, bot: Bot) -> None:
        for name, funcs in self._listener_functions.items():
            for func in funcs:
                bot._state.ping.add_listener(name, func)

        for cmd in self._commands:
            if isinstance(cmd, Command):
                cmd._state = bot._state
                cmd._state.commands.append(cmd)
            elif isinstance(cmd, Group):
                cmd._state = bot._state

        self.bot = bot

        self.bot._state.gears.append(self)
