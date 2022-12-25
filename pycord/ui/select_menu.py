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
from typing import Any, Literal

from ..arguments import ArgumentParser
from ..channel import identify_channel
from ..errors import ComponentException
from ..interaction import Interaction
from ..media import Emoji
from ..role import Role
from ..types import AsyncFunc
from ..undefined import UNDEFINED, UndefinedType
from ..user import User
from ..utils import remove_undefined
from .interactive_component import InteractiveComponent

arg_parser = ArgumentParser()


class SelectOption:
    """
    Create a new Select Menu Option

    Parameters
    ----------
    label: :class:`str`
        The label of this option
    description: :class:`str`
        The description of this option
    emoji: Union[:class:`str`, :class:`.Emoji`]
        The emoji to use in front of this option's label
    default: :class:`bool`
        Wether this is the default option or not.
        Defaults to False
    """

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

    def __bool__(self) -> bool:
        return self._resp is not None


class SelectMenu(InteractiveComponent):
    """
    Represents a Discord Select Menu
    """

    def __init__(
        self,
        callback: AsyncFunc,
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
        elif self.type == 5:
            users = []
            for user_id in inter.values:
                users.append(
                    User(inter.data['resolved']['users'][user_id], self._state)
                )

            await self._callback(
                inter, users if len(users) > 1 and users != [] else users[0]
            )
        elif self.type == 6:
            roles = []
            for role_id in inter.values:
                roles.append(
                    Role(inter.data['resolved']['roles'][role_id], self._state)
                )

            await self._callback(
                inter, roles if len(roles) > 1 and roles != [] else roles[0]
            )
        elif self.type == 7:
            mentionables = []
            for mentionable_id in inter.values:
                try:
                    mentionables.append(
                        User(
                            inter.data['resolved']['users'][mentionable_id], self._state
                        )
                    )
                except KeyError:
                    mentionables.append(
                        Role(inter.data['resolved']['roles'][mentionable_id])
                    )

            await self._callback(
                inter,
                mentionables
                if len(mentionables) > 1 and mentionables != []
                else mentionables[1],
            )
        elif self.type == 8:
            channels = []
            for channel_id in inter.values:
                channels.append(
                    identify_channel(
                        inter.data['resolved']['channels'][channel_id], self._state
                    )
                )

            await self._callback(
                inter, channels if len(channels) > 1 and channels != [] else channels[0]
            )

    def disable(self) -> None:
        """
        Disables this Select Menu
        """
        self.disabled = True
