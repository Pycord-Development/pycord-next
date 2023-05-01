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

from typing import Any
from uuid import uuid4

from ..enums import TextInputStyle
from ..interaction import Interaction
from ..missing import MISSING, MissingEnum
from ..types import AsyncFunc
from ..utils import remove_undefined
from .interactive_component import InteractiveComponent


class Modal:
    """
    Represents a Discord Modal
    Stores, deletes, uses, and calls Text Inputs

    Parameters
    ----------
    title: :class:`str`
        The title of this Modal in the Discord UI
    """

    def __init__(
        self,
        title: str,
    ) -> None:
        self.id = str(uuid4())
        self.title = title
        self.components: list[TextInput] = []
        self._callback: AsyncFunc | None = None

    def on_call(self) -> AsyncFunc:
        """
        Add a function to run when this Modal is submitted
        """

        def wrapper(func: AsyncFunc) -> AsyncFunc:
            self._callback = func
            return func

        return wrapper

    def add_text_input(self, text_input: TextInput) -> None:
        """
        Append a Text Input to this Modal

        Parameters
        ----------
        text_input: :class:`.TextInput`
            The text input to append
        """
        self.components.append(text_input)

    def _to_dict(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'custom_id': self.id,
            'components': [
                {'type': 1, 'components': [comp._to_dict() for comp in self.components]}
            ],
        }

    async def _invoke(self, inter: Interaction) -> None:
        comb = []
        for text_input in self.components:
            found = False
            for comp in inter.data['components'][0]['components']:
                if comp['custom_id'] == text_input.id:
                    comb.append(comp['value'])
                    found = True
            if found is False:
                comb.append(None)

        await self._callback(inter, *comb)


class TextInput(InteractiveComponent):
    """
    Represents a Text Input on a Modal

    Parameters
    ----------
    label: :class:`str`
        The label of this Text Input
    style: :class:`style`
        The style to use within this Text Input
    min_length: :class:`int`
        The minimum text length
    max_length: :class:`int`
        The maximum text length
    required: :class:`bool`
        Wether this Text Input is required to be filled or not
    value: :class:`str`
        The default value of this Text Input
    placeholder: :class:`str`
        The placeholder value to put onto this Text Input
    """

    def __init__(
        self,
        label: str,
        style: TextInputStyle | int,
        min_length: int | MissingEnum = MISSING,
        max_length: int | MissingEnum = MISSING,
        required: bool | MissingEnum = MISSING,
        value: str | MissingEnum = MISSING,
        placeholder: str | MissingEnum = MISSING,
    ) -> None:
        self.id = str(uuid4())
        self.label = label

        if isinstance(style, TextInputStyle):
            self._style = style.value
            self.style = style
        else:
            self._style = style
            self.style = style

        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value
        self.placeholder = placeholder

    def _to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            type=4,
            custom_id=self.id,
            label=self.label,
            style=self._style,
            min_length=self.min_length,
            max_length=self.max_length,
            required=self.required,
            value=self.value,
            placeholder=self.placeholder,
        )
