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

from ...embed import Embed
from ...snowflake import Snowflake
from ...types.component import Component
from ...types.message import Message
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined
from ..route import Route
from .base import BaseRouter


class Messages(BaseRouter):
    async def create_message(
        self,
        channel_id: Snowflake,
        content: str | UndefinedType = UNDEFINED,
        nonce: int | str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        sticker_ids: list[Snowflake] | UndefinedType = UNDEFINED,
        flags: int | UndefinedType = UNDEFINED,
        components: list[Component] | UndefinedType = UNDEFINED,
    ) -> Message:
        if embeds is not UNDEFINED:
            embeds = [embed._to_data() for embed in embeds]  # type: ignore

        return await self.request(  # type: ignore
            'POST',
            Route(f'/channels/{channel_id}/messages', channel_id=channel_id),
            data=remove_undefined(
                content=content,
                embeds=embeds,
                nonce=nonce,
                tts=tts,
                sticker_ids=sticker_ids,
                flags=flags,
                components=components,
            ),
        )
