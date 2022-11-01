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

import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeVar

from .api import HTTPClient

if TYPE_CHECKING:
    from .flags import Intents
    from .gateway import PassThrough

__all__ = ['State']


S = TypeVar('S')
D = TypeVar('D')


# TODO: Fix types
class StateStore:
    def __init__(self, stored: S) -> None:
        self._stored = stored
        self._store: dict[str, Any] = {}

    async def invoke(self, func: Callable | Coroutine, *args, **kwargs) -> S:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def select(self, id: str, default: D | None = None) -> S | D | None:
        return self._store.get(id, default=default)

    def capture(self, id: str, default: D | None = None) -> S | D | None:
        return self._store.pop(id, default=default)

    def insert(self, id: str, data: S) -> None:
        self._store[id] = data


class State:
    def __init__(self, **options: Any) -> None:
        self.token = options.get('token', '')
        self.max_messages: int = options.get('max_messages')
        self.http = HTTPClient(
            token=self.token,
            base_url=options.get('http_base_url', 'https://discord.com/api/v10'),
        )
        self.large_threshold: int = options.get('large_threshold', 250)
        self.shard_concurrency: PassThrough | None = None
        self.intents: Intents = options['intents']
        self.raw_user: dict[str, Any] | None = None
        self.storer = options.get('storer', StateStore)

    def reset(self) -> None:
        pass
