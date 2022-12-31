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

from typing import TYPE_CHECKING

from .api import HTTPClient, Route
from .embed import Embed
from .enums import WebhookType
from .guild import Guild
from .snowflake import Snowflake
from .types import Webhook as DiscordWebhook
from .undefined import UNDEFINED, UndefinedType
from .user import User
from .utils import remove_undefined

if TYPE_CHECKING:
    from .state import State


class Webhook:
    def __init__(self, id: int, token: str) -> None:
        self.id = Snowflake(id)
        self.token = token
        self._http = HTTPClient()

    async def execute(
        self,
        content: str | UndefinedType = UNDEFINED,
        username: str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[Embed] | UndefinedType = UNDEFINED,
        sticker_ids: list[Snowflake] | UndefinedType = UNDEFINED,
        flags: int | UndefinedType = UNDEFINED,
    ):
        if embeds is not UNDEFINED:
            embeds = [embed._to_data() for embed in embeds]

        return await self._http.request(
            'POST',
            Route(
                '/webhooks/{webhook_id}/{webhook_token}',
                webhook_id=self.id,
                webhook_token=self.token,
            ),
            data=remove_undefined(
                content=content,
                embeds=embeds,
                username=username,
                tts=tts,
                sticker_ids=sticker_ids,
                flags=flags,
            ),
        )


class GuildWebhook:
    def __init__(self, data: DiscordWebhook, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.type: WebhookType = WebhookType(data['type'])
        self.guild_id: Snowflake | None | UndefinedType = (
            Snowflake(data['guild_id'])
            if data.get('guild_id') is not None
            else data.get('guild_id', UNDEFINED)
        )
        self.channel_id: Snowflake | None | UndefinedType = (
            Snowflake(data['channel_id'])
            if data.get('channel_id') is not None
            else None
        )
        self.user: User | UndefinedType = (
            User(data['user'], state) if data.get('user') is not None else UNDEFINED
        )
        self.name: str | None = data['name']
        self._avatar: str | None = data['avatar']
        self.token: str | UndefinedType = data.get('token', UNDEFINED)
        self.application_id: Snowflake | None = (
            Snowflake(data['application_id'])
            if data.get('application_id') is not None
            else None
        )
        self.source_guild: Guild | UndefinedType = (
            Guild(data['source_guild'], state)
            if data.get('source_guild') is not None
            else UNDEFINED
        )
        self.url: str | UndefinedType = data.get('url', UNDEFINED)
