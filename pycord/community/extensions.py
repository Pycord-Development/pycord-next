# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 VincentRPS
# Copyright (c) 2022 Pycord Development Team
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
"""
pycord.community.extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Extensions which allow you to extend your bot across multiple files.

:copyright: 2021-2022 VincentRPS
:license: MIT, see LICENSE for more details.
"""

from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    from pycord.apps import app as appt


class Extension:
    def __init__(self):
        # NOTE: Stored simiar to EventDispatcher's one.
        self._listeners: dict[Any, list[Callable | Coroutine]] = {}
        self.app: appt = None  # type: ignore

    def listen(self, name: Any):
        def inner(func: Callable | Coroutine):
            if self._listeners.get(name):
                self._listeners[name].append(func)
            else:
                self._listeners[name] = [func]

        return inner

    def extend(self, app: "appt"):
        self.app = app
        for name, functions in self._listeners.items():
            for function in functions:
                app.dispatcher.add_listener(name=name, function=function)
