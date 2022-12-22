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
from typing import Any, Coroutine, Literal

from ..arguments import ArgumentParser
from ..errors import ComponentException
from ..interaction import Interaction
from ..media import Emoji
from ..undefined import UNDEFINED, UndefinedType
from ..utils import remove_undefined
from .interactive_component import InteractiveComponent

arg_parser = ArgumentParser()


class SelectOption:
    def __init__(
        self,
        label: str,
        description: str | UndefinedType = UNDEFINED,
        emoji: str | Emoji | UndefinedType = UNDEFINED,
        default: bool | UndefinedType = UNDEFINED,
    ) -> None:
        self.label = label
        self.description = description
        self.default = default
        self.value: str | None = None
        if isinstance(emoji, str):
            self.emoji = Emoji._from_str(emoji, None)
        else:
            self.emoji = emoji

        self._resp: str | None = None

    def _to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            label=self.label,
            description=self.description,
            emoji=self.emoji._partial() if self.emoji else UNDEFINED,
            value=self.value,
            default=self.default,
        )

    def __get__(self) -> str:
        return self._resp

    def clone(self, resp: str) -> 'SelectOption':
        c = copy(self)
        c._resp = resp
        return c

    def __bool__(self) -> bool:
        return self._resp is not None


class SelectMenu(InteractiveComponent):
    def __init__(
        self,
        callback: Coroutine,
        custom_id: str,
        type: Literal[3, 5, 6, 7, 8] = 3,
        channel_types: list[int] | UndefinedType = UNDEFINED,
        placeholder: str | UndefinedType = UNDEFINED,
        min_values: int | UndefinedType = UNDEFINED,
        max_values: int | UndefinedType = UNDEFINED,
        disabled: bool | UndefinedType = UNDEFINED,
    ) -> None:
        super().__init__(callback, custom_id)
        self.type = type
        self.options: list[SelectOption] = []
        self.channel_types = channel_types
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

        # per-type checks
        if channel_types and type != 8:
            raise ComponentException(
                'channel_types must only be put on type eight select menus'
            )

        self._options_dict: dict[str, Any] = {}
        self.parse_arguments()

    def _to_dict(self) -> dict[str, Any]:
        return remove_undefined(
            type=self.type,
            custom_id=self.id,
            channel_types=self.channel_types,
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            disabled=self.disabled,
            options=[option._to_dict() for option in self.options],
        )

    def parse_arguments(self) -> None:
        defaults = arg_parser.get_arg_defaults(self._callback)

        for name, arg in defaults.items():
            if not isinstance(arg[0], SelectOption) and arg[1] != Interaction:
                print(arg[0])
                raise ComponentException(
                    'Parameters on Select Menu callbacks must only be SelectOptions and Interaction'
                )
            elif self.type != 3 and isinstance(arg[0], SelectOption):
                raise ComponentException(
                    'Options may only be put on type three Select Menus'
                )

            if arg[1] == Interaction:
                continue

            option = arg[0]
            option.value = name
            self.options.append(option)
            self._options_dict[name] = option

    async def _internal_invocation(self, inter: Interaction) -> None:
        if self.type == 3:
            invocation_data: dict[str, bool] = {}
            for value in inter.values:
                invocation_data[value] = True
            for option in self.options:
                if option.value not in invocation_data:
                    invocation_data[option.value] = False

            await self._callback(inter, **invocation_data)

    def disable(self) -> None:
        self.disabled = True
