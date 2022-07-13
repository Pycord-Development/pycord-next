# Copyright (c) 2021-2022 VincentRPS
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

from asyncio import create_task, get_running_loop, iscoroutinefunction
from typing import Any, Callable, Coroutine


# TODO: wait_for with timeout.
class EventDispatcher:
    def __init__(self) -> None:
        self.events: dict[Any, list[Coroutine | Callable]] = {}

    async def _dispatch_under_names(self, event_name: Any, *args, **kwargs) -> None:
        t = 'temp-' + event_name

        temporary_events = self.events.get(t)

        if temporary_events is not None:
            for event in temporary_events:
                if iscoroutinefunction(event):
                    await event(*args, **kwargs)  # type: ignore
                else:
                    loop = get_running_loop()
                    await loop.run_in_executor(None, event(*args, **kwargs))  # type: ignore

            self.events.pop(t)

        events = self.events.get(event_name)

        if events is None:
            return

        for event in events:
            if iscoroutinefunction(event):
                await event(*args, **kwargs)  # type: ignore
            else:
                loop = get_running_loop()
                await loop.run_in_executor(None, event(*args, **kwargs))  # type: ignore

    def dispatch(self, event: Any, *args, **kwargs):
        create_task(self._dispatch_under_names(event, *args, **kwargs))

    def add_listener(self, name: Any, function: Coroutine | Callable):
        if self.events.get(name):
            self.events[name].append(function)
        else:
            self.events[name] = [function]

    def remove_listener(self, name: Any, function: Coroutine | Callable):
        if self.events.get(name):
            self.events[name].remove(function)
