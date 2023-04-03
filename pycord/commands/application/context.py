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

from ...embed import Embed
from ...flags import MessageFlags
from ...interaction import Interaction
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined

if TYPE_CHECKING:
    from ...state import State
    from ...types import Interaction as InteractionData


class Context(Interaction):
    """
    Contextual prelude to Interactions.
    """

    def __init__(self, data: InteractionData, state: State, _: Any = None) -> None:
        super().__init__(data, state, response=True)

    async def defer(self) -> None:
        """
        Defer this interaction. Only defers if not deferred.
        """

        if not self.response._deferred:
            await self.response.defer()

    async def send(
        self,
        content: str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        flags: int | MessageFlags | UndefinedType = UNDEFINED,
        ephemeral: bool | UndefinedType = UNDEFINED,
    ) -> None:
        """
        Respond to an interaction.

        **Can only send once, if more needs to be done, use .send**

        Parameters
        ----------
        content: :class:`str`
            The message content to send.
        tts: :class:`bool`
            Whether TTS should be enabled for this message.
        embeds: :class:`list`[:class:`.Embed`]
            The embeds to send in this response.
        flags: :class:`int` | :class:`.MessageFlags`
            The flags to include in this message.
        ephemeral: :class:`bool`
            Whether to ephermalize this message or not.
        """

        if self.response.responded:
            if ephemeral:
                if not isinstance(flags, MessageFlags):
                    if not flags:
                        flags = MessageFlags()
                    else:
                        flags = MessageFlags.from_value(flags)

                flags.ephemeral = True

            await self.response.followup.send(
                **remove_undefined(content=content, tts=tts, embeds=embeds, flags=flags)
            )
        else:
            await self.respond(
                **remove_undefined(content=content, tts=tts, embeds=embeds, flags=flags)
            )

    async def respond(
        self,
        content: str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        flags: int | MessageFlags | UndefinedType = UNDEFINED,
        ephemeral: bool | UndefinedType = UNDEFINED,
    ) -> None:
        """
        Respond to an interaction.

        **Can only send once, if more needs to be done, use .send**

        Parameters
        ----------
        content: :class:`str`
            The message content to send.
        tts: :class:`bool`
            Whether TTS should be enabled for this message.
        embeds: :class:`list`[:class:`.Embed`]
            The embeds to send in this response.
        flags: :class:`int` | :class:`.MessageFlags`
            The flags to include in this message.
        ephemeral: :class:`bool`
            Whether to ephermalize this message or not.
        """

        if ephemeral:
            if not isinstance(flags, MessageFlags):
                if not flags:
                    flags = MessageFlags()
                else:
                    flags = MessageFlags.from_value(flags)

            flags.ephemeral = True

        await self.response.send(
            **remove_undefined(content=content, tts=tts, embeds=embeds, flags=flags)
        )
