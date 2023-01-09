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
import inspect
from types import SimpleNamespace
from typing import TYPE_CHECKING, Type

from pycord import events

from ..types import AsyncFunc

if TYPE_CHECKING:
    from ..state import State


class BaseEmitted(SimpleNamespace):
    EVENT_NAME: str

    @classmethod
    async def _load(self, *args, **kwargs) -> None:
        ...


class Emitter:
    def __init__(self, state: State) -> None:
        self._state = state
        self._events: dict[str, tuple[Type[BaseEmitted], AsyncFunc]] = {}
        self._temporary_events: dict[str, tuple[Type[BaseEmitted], AsyncFunc]] = {}

        for _, obj in inspect.getmembers(events):
            if inspect.isclass(obj):
                if obj.__class__ == BaseEmitted or obj.__class__ == events.BaseEvent:
                    self._events[obj.EVENT_NAME] = (obj, None)

    async def dispatch(self, name_: str, **kwargs) -> None:
        name = f'on_{name_.lower()}'

        commands = kwargs.pop('commands', [])

        for event in self._events.get(name, []):
            if event[1] is None:
                parent: list[BaseEmitted] = await event[0]._load(
                    self._state, kwargs['_raw_data']
                )

                for child in parent:
                    name = child.EVENT_NAME
                    searchable = child.__class__

                    for event in self._events.get(name):
                        if event[0] == searchable:
                            asyncio.create_task(event[1](child))

                    for event in self._temporary_events.get(name):
                        if event[0] == searchable:
                            asyncio.create_task(event[1](child))

                continue

            asyncio.create_task(
                event[1](await event[0]._load(self._state, kwargs['_raw_data']))
            )

        for event in self._temporary_events.get(name, []):
            if event[1] is None:
                parent: list[BaseEmitted] = await event[0]._load(
                    self._state, kwargs['_raw_data']
                )

                for child in parent:
                    name = child.EVENT_NAME
                    searchable = child.__class__

                    for event in self._events.get(name):
                        if event[0] == searchable:
                            asyncio.create_task(event[1](child))

                    for event in self._temporary_events.get(name):
                        if event[0] == searchable:
                            asyncio.create_task(event[1](child))

                continue

            asyncio.create_task(
                event[1](await event[0]._load(self._state, kwargs['_raw_data']))
            )

            self._temporary_pings[name].remove(event)

        # TODO: handle commands
        # or move them to the InteractionCreate event
        for command in commands:
            ...

    def add_events(self) -> None:
        ...

    def add_listener(self, event: Type[BaseEmitted], func: AsyncFunc) -> None:
        name = event.EVENT_NAME

        if self._events.get(name):
            self._events[name].append((event, func))
        else:
            self._events[name] = [(event, func)]
