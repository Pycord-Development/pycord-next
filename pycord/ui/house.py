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

from copy import copy
from typing import Coroutine
from uuid import uuid4

from ..enums import ButtonStyle
from ..media import Emoji
from ..undefined import UNDEFINED, UndefinedType
from .button import Button
from .component import ActionRow, Component


class House:
    def __init__(self) -> None:
        self.components: dict[Component, Component] = {}

    def disabled(self) -> 'House':
        c = copy(self)
        c.components = {}

        for _, comp in self.components.items():
            cc = copy(comp)
            cc.disable()
            c.components[cc] = cc

        return c

    def action_row(self) -> ActionRow:
        return ActionRow(components=[c._to_dict() for _, c in self.components.items()])

    def add_component(self, comp: Component) -> None:
        self.components[comp] = comp

    def remove_component(self, comp: Component) -> None:
        del self.components[comp]

    def button(
        self,
        style: ButtonStyle | int,
        label: str | None,
        emoji: str | Emoji | UndefinedType = UNDEFINED,
        url: str | UndefinedType = UNDEFINED,
        disabled: bool = False,
    ) -> Button:
        def wrapper(func: Coroutine) -> Button:
            if not url:
                custom_id = str(uuid4())
            else:
                custom_id = UNDEFINED
            button = Button(
                func,
                style=style,
                label=label,
                emoji=emoji,
                url=url,
                disabled=disabled,
                custom_id=custom_id,
            )
            self.add_component(button)
            return button

        return wrapper
