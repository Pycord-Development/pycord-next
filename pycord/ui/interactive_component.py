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

from typing import TYPE_CHECKING

from .component import Component

if TYPE_CHECKING:
    from ..interaction import Interaction
    from ..state import State
    from ..types import AsyncFunc


class InteractiveComponent(Component):
    """
    The base set of a component which can be interacted with.

    .. WARNING::
        This is a **base class** which means we don't
        recommend usage of it unless you're making your
        own component class.
    """

    def __init__(
        self,
        callback: AsyncFunc,
        custom_id: str | None,
    ) -> None:
        self._callback = callback
        self.id = custom_id
        self._state: State | None = None

    def _set_state(self, state: State) -> None:
        self._state = state

    async def _internal_invocation(self, inter: Interaction) -> None:
        ...

    async def _invoke(self, inter: Interaction) -> None:
        if inter.type not in (3, 5):
            return

        custom_id = inter.data['custom_id']

        if custom_id == self.id:
            await self._internal_invocation(inter)
