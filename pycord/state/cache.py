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

import gc
import logging
import weakref
from collections import OrderedDict
from typing import Any, Literal, Type, TypeVar, cast

_log = logging.getLogger()

T = TypeVar("T")


class Store:
    """The default Pycord store."""

    def __init__(self, max_items: int = 0) -> None:
        self._store: OrderedDict[Any, Any] = OrderedDict()
        self._weak_store: dict[Any, weakref.ReferenceType[Any]] = {}
        self.max_items = max_items
        gc.callbacks.append(self.__garbage_collector)

    async def get(self, key: Any, *, t: T) -> T | None:
        ival = self._store.get(key)

        if ival:
            return cast(T, ival)

        weak_val = self._weak_store.get(key)

        if weak_val is not None and weak_val() is not None:
            return cast(T, weak_val())

        return None

    async def upsert(
        self, key: Any, object: Any, *, extra_keys: list[Any] | None = None
    ) -> None:
        self._store[key] = object

        if extra_keys:
            ref = weakref.ref(object)
            for key in extra_keys:
                self._weak_store[key] = ref

    async def delete(self, key: Any) -> None:
        del self._store[key]

    def __garbage_collector(
        self, phase: Literal["start", "stop"], info: dict[str, int]
    ) -> None:
        """Collect all weakrefs which are no longer in use."""

        del info

        if phase == "stop":
            return

        _log.debug("cleaning up weak references")

        if self.max_items != 0 and len(self._store) > self.max_items:
            for _ in range(len(self._store) - self.max_items):
                self._store.popitem()

        for key, ref in self._weak_store.copy().items():
            if ref() is None:
                _log.debug(f"removing {key} from weak store")
                del self._weak_store[key]

    async def close(self) -> None:
        gc.callbacks.remove(self.__garbage_collector)


class CacheStore:
    def __init__(self, store_class: Type[Store]) -> None:
        self._stores: dict[str, Store] = {}
        self._store_class = store_class

    def __setitem__(self, key: str, val: int) -> None:
        self._stores[key] = self._store_class(val)

    def __getitem__(self, key: str) -> Store:
        istore = self._stores.get(key)

        if istore:
            return istore
        else:
            store = self._store_class()
            self._stores[key] = store
            return store
