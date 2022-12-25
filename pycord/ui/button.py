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

from typing import TYPE_CHECKING, Any

from ..enums import ButtonStyle
from ..errors import ComponentException
from ..media import Emoji
from ..types import AsyncFunc
from ..undefined import UNDEFINED, UndefinedType
from ..utils import remove_undefined
from .interactive_component import InteractiveComponent

if TYPE_CHECKING:
    from ..interaction import Interaction


class Button(InteractiveComponent):
    """
    Represents a Discord Button
    """

    def __init__(
        self,
        callback: AsyncFunc,
        # button-based values
        style: ButtonStyle | int,
        label: str | UndefinedType = UNDEFINED,
        custom_id: str | UndefinedType = UNDEFINED,
        emoji: str | Emoji | UndefinedType = UNDEFINED,
        url: str | UndefinedType = UNDEFINED,
        disabled: bool = False,
    ) -> None:
        super().__init__(callback, custom_id)
        if isinstance(style, ButtonStyle):
            self._style = style.value
        else:
            self._style = style
        self.style = style
        self.label: str | None | UndefinedType = label
        self.url = url

        if label is None and url is None:
            raise ComponentException('label and url cannot both be None')

        if url and custom_id:
            raise ComponentException('Cannot have custom_id and url at the same time')

        if label is None:
            self.label = UNDEFINED

        if isinstance(emoji, str):
            self.emoji = Emoji._from_str(emoji, None)
        else:
            self.emoji = emoji

        self.disabled = disabled

    def _to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            **{
                'style': self._style,
                'label': self.label,
                'url': self.url,
                'custom_id': self.id,
                'emoji': self.emoji._partial() if self.emoji else UNDEFINED,
                'disabled': self.disabled,
                'type': 2,
            }
        )

    def disable(self) -> None:
        """
        Disables this Button
        """
        self.disabled = True

    async def _internal_invocation(self, inter: Interaction) -> None:
        await self._callback(inter)
