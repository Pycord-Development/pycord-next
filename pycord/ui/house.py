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
from typing import Literal
from uuid import uuid4

from ..enums import ButtonStyle, SelectMenuType
from ..errors import ComponentException
from ..media import Emoji
from ..types import AsyncFunc
from ..undefined import UNDEFINED, UndefinedType
from .button import Button
from .component import ActionRow, Component
from .select_menu import SelectMenu


class House:
    """
    The house for components.
    You can have, at maximum, **five** houses on one message
    """

    def __init__(self) -> None:
        self.components: dict[Component, Component] = {}

    def disabled(self) -> House:
        """
        Returns a copy of this House in which all components are disabled
        """
        c = copy(self)
        c.components = {}

        for _, comp in self.components.items():
            cc = copy(comp)
            cc.disable()
            c.components[cc] = cc

        return c

    def action_row(self) -> ActionRow:
        """
        A representation of this house within an action row.
        """
        return ActionRow(components=[c._to_dict() for _, c in self.components.items()])

    def add_component(self, comp: Component) -> None:
        """
        Append a component to this House's store

        Parameters
        ----------
        comp: :class:`.Component`
            The component to append
        """
        if len(self.components) == 5:
            raise ComponentException('Cannot add more components, already reached maximum')

        self.components[comp] = comp

    def remove_component(self, comp: Component) -> None:
        """
        Remove a component from this House's store

        Parameters
        ----------
        comp: :class:`.Component`
            The component to remove
        """
        del self.components[comp]

    def button(
        self,
        style: ButtonStyle | int,
        label: str | None,
        emoji: str | Emoji | UndefinedType = UNDEFINED,
        url: str | UndefinedType = UNDEFINED,
        disabled: bool = False,
    ) -> Button:
        """
        Create a new button within this house

        Parameters
        ----------
        style: Union[:class:`.ButtonStyle`, :class:`int`]
            The style of button to use
        label: Union[:class:`str`, None]
            The label to use for this button
        emoji: Union[:class:`str`, :class:`.Emoji`]
            The emoji to use in front of this button's label
        url: :class:`str`
            The URL of this button
        disabled: :class:`bool`
            Wether if this button shall be started disabled or not.
            Defaults to `False`.
        """

        def wrapper(func: AsyncFunc) -> Button:
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

    def select_menu(
        self,
        type: Literal[3, 5, 6, 7, 8] | SelectMenuType = 3,
        channel_types: list[int] | UndefinedType = UNDEFINED,
        placeholder: str | UndefinedType = UNDEFINED,
        min_values: int | UndefinedType = UNDEFINED,
        max_values: int | UndefinedType = UNDEFINED,
        disabled: bool | UndefinedType = UNDEFINED,
    ) -> SelectMenu:
        """
        Create a new Select Menu within this House

        Parameters
        ----------
        type: Union[:class:`int`, :class:`.SelectMenuType`]
            The type of Select Menu to instantiate
        channel_types: list[:class:`int`]
            A list of channel types to limit this select menu to
        placeholder: :class:`str`
            The placeholder value to put
        min_values: :class:`int`
            The minimum number of values allowed
        max_values: :class:`int`
            The maximum number of values allowed
        disabled: :class:`bool`
            Wether if this select menu shall be started disabled or not.
            Defaults to `False`.
        """
        if isinstance(type, SelectMenuType):
            type = type.value

        def wrapper(func: AsyncFunc) -> SelectMenu:
            custom_id = str(uuid4())
            select = SelectMenu(
                func,
                custom_id=custom_id,
                type=type,
                channel_types=channel_types,
                placeholder=placeholder,
                min_values=min_values,
                max_values=max_values,
                disabled=disabled,
            )
            self.add_component(select)
            return select

        return wrapper
