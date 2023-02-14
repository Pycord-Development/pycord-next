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
from asyncio import Future
from typing import TYPE_CHECKING, Any, Type, TypeVar

from ..types import AsyncFunc

if TYPE_CHECKING:
    from ..state import State


T = TypeVar('T', bound='Event')


class Event:
    _name: str
    _state: 'State'

    async def _is_publishable(self, data: dict[str, Any], state: 'State') -> bool:
        return True

    async def _async_load(self, data: dict[str, Any], state: 'State') -> None:
        ...


class EventManager:
    def __init__(self, base_events: list[Type[Event]], state: 'State') -> None:
        self._base_events = base_events
        self._state = state

        # structured like:
        # EventClass: [childrenfuncs]
        self.events: dict[Type[Event], list[AsyncFunc]] = {}

        for event in self._base_events:
            # base_events is used for caching purposes
            self.events[event] = []

        self.wait_fors: dict[Type[Event], list[Future[Event]]] = {}

    def add_event(self, event: Type[Event], func: AsyncFunc) -> None:
        try:
            self.events[event].append(func)
        except KeyError:
            self.events[event] = [func]

    def wait_for(self, event: Type[T]) -> Future[T]:
        fut: Future[event] = Future()

        try:
            self.wait_fors[event].append(fut)  # type: ignore
        except KeyError:
            self.wait_fors[event] = [fut]  # type: ignore

        return fut

    async def publish(self, event_str: str, data: dict[str, Any]) -> None:
        for event, funcs in self.events.items():
            if event._name == event_str:  # type: ignore
                eve = event()
                dispatch = await eve._is_publishable(data, self._state)  # type: ignore

                # used in cases like GUILD_AVAILABLE
                if dispatch is False:
                    continue
                else:
                    await eve._async_load(data, self._state)  # type: ignore

                eve._state = self._state  # type: ignore

                for func in funcs:
                    asyncio.create_task(func(eve))

                wait_fors = self.wait_fors.get(event)

                if wait_fors is not None:
                    for wait_for in wait_fors:
                        wait_for.set_result(eve)
                    self.wait_fors.pop(event)

                for command in self._state.commands:
                    if command._processor_event == event:  # type: ignore
                        asyncio.create_task(command._invoke(eve))  # type: ignore
