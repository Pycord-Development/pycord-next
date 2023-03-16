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

import asyncio
from copy import copy
from typing import TYPE_CHECKING
from uuid import uuid4

import typing_extensions
from option import Err, Ok, Result

from ..commands.application.prelude import Prelude
from ..events.other import InteractionInvoke, WaitForMessage
from ..undefined import UNDEFINED, UndefinedType
from .base_component import Component

if TYPE_CHECKING:
    from ..message import Message


class View:
    """
    User-defined view of components.
    Gear-like in structure.
    """

    def __init__(self, default_timeout: int | None = 180) -> None:
        self._default_timeout = default_timeout
        self._components: list[Component] = []
        self._custom_id = None
        self._timeout = None
        self._timeout_secs = None

    def _time_out(self) -> None:
        """Called when a view has gotten timed out or cancelled."""

    def __call__(self, custom_id: str | None = None) -> typing_extensions.Self:
        """
        Copy the View, and enable it with this custom id.
        """
        cls = copy(self)
        if custom_id:
            cls._custom_id = custom_id
        else:
            cls._custom_id = str(uuid4())
        return cls

    def overwatch(
        self, message: Message, timeout: int | None | UndefinedType = UNDEFINED
    ) -> Result[None, str]:
        """
        Watch over a message for interactions.
        """

        if self._custom_id is None:
            return Err('Must be initialized to use View')

        if timeout is UNDEFINED:
            timeout = self._default_timeout

        self._timeout_secs = timeout

        if message.author.id != message._state.user.id:
            return Err('Cannot overwatch a message not sent by the bot user')

        self._timeout = asyncio.Timeout(timeout)

        self._inter_invoke = InteractionInvoke(self._custom_id, Prelude)
        message._state.event_manager.add_event(self._inter_invoke, self._invoke)
        self._message = message
        asyncio.create_task(self.__loop_for_timeout())

        return Ok(None)

    async def __loop_for_timeout(self) -> None:
        try:
            # run until timeout occurs
            async with self._timeout:
                await asyncio.Future()
        except asyncio.TimeoutError:
            await self._time_out()

    async def _invoke(self, prelude: Prelude) -> None:
        if not self._timeout.expired():
            self._timeout.reschedule(self)
        else:
            self._message._state.event_manager.remove_event(
                self._inter_invoke, self._invoke
            )
            return
