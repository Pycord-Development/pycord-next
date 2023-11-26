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


import asyncio
from typing import Any

from aiohttp import BasicAuth

from .state.cache import Store
from .state.core import BASE_MODELS, State


class Bot:
    def __init__(
        self,
        token: str,
        intents: int,
        shards: list[int] | range | None = None,
        max_message_cache: int = 10000,
        max_member_cache: int = 50000,
        base_url: str = "https://discord.com/api/v10",
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
        store_class: type[Store] = Store,
        model_classes: dict[Any, Any] = BASE_MODELS,
    ) -> None:
        self.state = State(
            token=token,
            max_messages=max_message_cache,
            max_members=max_member_cache,
            intents=intents,
            base_url=base_url,
            proxy=proxy,
            proxy_auth=proxy_auth,
            store_class=store_class,
            cache_model_classes=model_classes,
            shards=shards,
        )

    async def start(self) -> None:
        await self.state.http.force_start()
        await self.state.gateway.start()

        try:
            await asyncio.Future()
        except (asyncio.CancelledError, KeyboardInterrupt):
            await self.state.http._session.close()
            return
