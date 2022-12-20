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

from collections.abc import Iterator, Sequence
from itertools import accumulate
from typing import Any, Literal, TypeVar

from aiohttp import ClientResponse

from .undefined import UNDEFINED, UndefinedType

try:
    import msgspec
except ImportError:
    import json

    msgspec = None

DISCORD_EPOCH: int = 1420070400000
S = TypeVar('S', bound=Sequence)


async def _text_or_json(cr: ClientResponse, self) -> str | dict[str, Any]:
    if cr.content_type == 'application/json':
        return await cr.json(encoding='utf-8', loads=self._json_decoder)
    return await cr.text('utf-8')


def loads(data: Any) -> Any:
    return msgspec.json.decode(data.encode()) if msgspec else json.loads(data)


def dumps(data: Any) -> str:
    return msgspec.json.encode(data).decode('utf-8') if msgspec else json.dumps(data)


def parse_errors(errors: dict[str, Any], key: str | None = None) -> dict[str, str]:
    ret = []

    for k, v in errors.items():
        kie = f'{k}.{key}' if key else k

        if isinstance(v, dict):
            try:
                errors_ = v['_errors']
            except KeyError:
                continue
            else:
                ret.append((kie, ''.join(x.get('message') for x in errors_)))
        else:
            ret.append((kie, v))

    return dict(ret)


def chunk(items: S, n: int) -> Iterator[S]:
    """Groups ``items`` into ``n`` chunks.

    Parameters
    ----------
    items: S
        A :class:`Sequence` of items to chunk.
    n: int
        The total number of chunks to create.

    Returns
    -------
    Iterator[S]
        An iterator of :class:`Sequence`s of items. Each :class:`Sequence` represents a chunk.
    """
    per_section, extras = divmod(len(items), n)
    sections = list(
        accumulate([0] + extras * [per_section + 1] + (n - extras) * [per_section])
    )
    for start, end in zip(sections, sections[1:]):
        yield items[start:end]  # type: ignore


def remove_undefined(**kwargs) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not UNDEFINED}
