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


from .store import Store


class GroupedStore:
    def __init__(self, **max_items) -> None:
        self._stores = []
        self._stores_dict = {}
        self._kwargs = max_items

    def get_stores(self) -> list[Store]:
        return self._stores

    def get_store(self, name: str) -> Store:
        return self._stores[name]

    def discard(self, name: str) -> None:
        d = self._stores_dict.get(name)
        if d is not None:
            self._stores_dict.pop(name)
            self._stores.remove(d)

    def sift(self, name: str) -> Store:
        s = self._stores_dict.get(name)
        if s is not None:
            return s

        for k, v in self._kwargs.items():
            if k == (name + '_max_items'):
                store = Store(v)
        else:
            store = Store()

        self._stores.append(store)
        self._stores_dict[name] = store
        return store
