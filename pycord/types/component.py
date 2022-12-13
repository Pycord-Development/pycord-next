# cython: language_level=3
# Copyright (c) 2022-present Pycord Development
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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .channel import CTYPE
from .media import Emoji

COTYPE = Literal[1, 2, 3, 4, 5, 6, 7, 8]
BSTYLE = Literal[1, 2, 3, 4, 5]


class ActionRow(TypedDict):
    components: list[Button | SelectMenu | TextInput]


class Button(TypedDict):
    type: Literal[2]
    style: BSTYLE
    label: NotRequired[str]
    emoji: NotRequired[Emoji]
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]


class SelectOption(TypedDict):
    label: str
    value: str
    description: NotRequired[str]
    emoji: NotRequired[Emoji]
    default: NotRequired[bool]


class SelectMenu(TypedDict):
    type: Literal[3, 5, 6, 7, 8]
    custom_id: str
    options: NotRequired[list[SelectOption]]
    channel_types: CTYPE
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    mazx_values: NotRequired[int]
    disabled: NotRequired[bool]


class TextInput(TypedDict):
    type: Literal[4]
    custom_id: str
    style: Literal[1, 2]
    label: str
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]


Component = ActionRow | SelectMenu | TextInput | Button
