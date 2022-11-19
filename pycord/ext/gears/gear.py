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

from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from ...commands import Command, Group

if TYPE_CHECKING:
    from ...bot import Bot

T = TypeVar('T')


class Gear:
    def __init__(self, name: str) -> None:
        self.name = name
        self._listener_functions: dict[str, list[Coroutine]] = {}
        self.bot: Bot
        self._commands: list[Command | Group] = []

    def listen(self, name: str) -> T:
        def wrapper(func: T) -> T:
            if self._listener_functions.get(name):
                self._listener_functions[name].append(func)
            else:
                self._listener_functions[name] = [func]
            return func

        return wrapper

    def command(self, name: str, cls: type[Command], **kwargs: Any) -> T:
        def wrapper(func: T) -> T:
            command = cls(func, name, None, **kwargs)
            self._commands.append(command)
            return command

        return wrapper

    def group(self, name: str, cls: type[Group], **kwargs: Any) -> T:
        def wrapper(func: T) -> T:
            r = cls(func, name, None, **kwargs)
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
