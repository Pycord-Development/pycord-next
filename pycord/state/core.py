# MIT License
#
# Copyright (c) 2023 Pycord
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
# SOFTWARE.

from typing import Any, Type

from aiohttp import BasicAuth

from ..internal.gateway import Gateway
from ..internal.http import HTTPClient
from .cache import CacheStore, Store

_BASE_MODELS: dict[Any, Any] = {}


class State:
    """The central bot cache."""

    def __init__(
        self,
        token: str,
        # cache-options
        max_messages: int,
        max_members: int,
        intents: int,
        # "advanced" options
        base_url: str = "https://discord.com/api/v10",
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
        # classes
        store_class: Type[Store] = Store,
        cache_model_classes: dict[Any, Any] = _BASE_MODELS,
    ) -> None:
        self._token = token
        self.cache = CacheStore(store_class)
        self.cache["messages"] = max_messages
        self.cache["members"] = max_members
        self.max_members = max_members
        self.intents = intents
        self.http = HTTPClient(token, base_url, proxy, proxy_auth)
        self.gateway = Gateway(self)
        self.cache_models = cache_model_classes
