# MIT License
#
# Copyright (c) 2023 Pycord
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
# SOFTWARE.


import asyncio
from typing import Any, Callable, Coroutine, Self, Type

from mypy_extensions import i16, mypyc_attr, trait

from ..task_descheduler import tasks


class Filters:
    def __init__(self, cls: Type["EventTrait"], filters: dict[str, Any] | None) -> None:
        self.event = cls
        self.filters = filters or {}


@trait
@mypyc_attr(allow_interpreted_subclasses=True)
class EventTrait:
    _name: str = "UNDEFINED"

    async def on(self, data: dict[str, Any], filters: Filters) -> Self:
        return self

    @classmethod
    def filter(cls, **filters: Any) -> Filters:
        return Filters(cls, filters)


EventFunc = Callable[[EventTrait], Coroutine[Any, Any, None]]


class EventManager:
    def __init__(self) -> None:
        self._events: dict[Type[EventTrait], list[tuple[Filters, EventFunc]]] = {}

    async def push(self, name: str, data: dict[str, Any]) -> i16:
        ret = 0
        async with tasks() as tg:
            for event, funcs in self._events.copy().items():
                e = event()
                if event._name == name:
                    for filt, func in funcs:
                        ret += 1
                        res = await e.on(data, filt)
                        tg[asyncio.create_task(func(res))]

        return ret

    def add_event(self, event: Type[EventTrait] | Filters, func: EventFunc) -> None:
        if isinstance(event, Filters):
            event_class = event.event
            filters = event.filters
        else:
            event_class = event
            filters = {}

        if event_class in self._events:
            self._events[event_class].append((Filters(event_class, filters), func))
        else:
            self._events[event_class] = [(Filters(event_class, filters), func)]

    def remove_event(self, event: Type[EventTrait] | Filters, func: EventFunc) -> None:
        if isinstance(event, Filters):
            event_class = event.event
        else:
            event_class = event

        if event_class in self._events:
            for f, func in self._events[event_class]:
                if func == func:
                    self._events[event_class].remove((f, func))
                    break
