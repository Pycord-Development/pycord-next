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

from typing import TYPE_CHECKING, Callable, TypeVar

from .command import Command

if TYPE_CHECKING:
    from ..state import State
    from ..types import AsyncFunc

T = TypeVar('T', bound=AsyncFunc)


class Group:
    def __init__(self, func: AsyncFunc | None, name: str, state: State) -> None:
        self.commands: list[Command] = []
        # nested groups
        self.groups: list['Group'] = []

        self.name = name
        self._callback = func
        self.__state = state
        self._pending_commands: list[Command] = []

    @property
    def _state(self) -> State:
        return self.__state

    @_state.setter
    def _state(self, state: State) -> None:
        self.__state = state

        for command in self._pending_commands:
            self._state.commands.append(command)

    def command(self, name: str) -> Callable[..., AsyncFunc]:
        def wrapper(func: T) -> T:
            command = Command(func, name=name, state=self._state, group=self)
            if self._state:
                self._state.commands.append(command)
            else:
                self._pending_commands.append(command)
            return func

        return wrapper
