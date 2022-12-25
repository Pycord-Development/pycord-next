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
from dataclasses import dataclass, field
from typing import Any, Literal


class Component:
    """
    The base component type which every other component
    subclasses and bases off of
    """

    id: str
    type: int
    disabled: bool

    def copy(self) -> Component:
        return copy(self)

    def _to_dict(self) -> dict[str, Any]:
        ...

    def disable(self) -> None:
        ...


@dataclass
class ActionRow:
    """
    Represents a Discord Action Row
    """

    type: Literal[1] = field(default=1)
    components: list[Component] = field(default=list)

    def _to_dict(self) -> dict[str, Any]:
        return {'type': self.type, 'components': self.components}
