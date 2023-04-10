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

import base64
import functools
import inspect
import warnings
from collections.abc import Iterator, Sequence
from itertools import accumulate
from typing import Any, AsyncGenerator, Callable, Type, TypeVar

from aiohttp import ClientResponse

from .file import File
from .types import AsyncFunc
from .missing import MISSING

try:
    import msgspec
except ImportError:
    import json

    msgspec = None

DISCORD_EPOCH: int = 1420070400000
S = TypeVar('S', bound=Sequence)
T = TypeVar('T')


async def _text_or_json(cr: ClientResponse) -> str | dict[str, Any]:
    if cr.content_type == 'application/json':
        return await cr.json(encoding='utf-8', loads=loads)
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
    return {k: v for k, v in kwargs.items() if v is not MISSING}


async def get_iterated_data(iterator: AsyncGenerator) -> list[Any]:
    hold = []

    async for data in iterator:
        hold.append(data)

    return hold


def get_arg_defaults(fnc: AsyncFunc) -> dict[str, tuple[Any, Any]]:
    signature = inspect.signature(fnc)
    ret = {}
    for k, v in signature.parameters.items():
        if (
            v.default is not inspect.Parameter.empty
            and v.annotation is not inspect.Parameter.empty
        ):
            ret[k] = (v.default, v.annotation)
        elif v.default is not inspect.Parameter.empty:
            ret[k] = (v.default, None)
        elif v.annotation is not inspect.Parameter.empty:
            ret[k] = (None, v.annotation)
        else:
            ret[k] = (None, None)

    return ret


async def find(cls: Type[T], *args: Any, **kwargs: Any) -> T:
    """
    Locates an object by either getting it from the cache, or
    fetching it from the API.

    Parameters
    ----------
    cls: Type[T]
        The class to get or fetch
    args: Any
        The arguments to insert in the get or fetch
    kwargs: Any
        The keyword arguments to insert in the get or fetch

    Usage
    -----

    .. TODO:: Make .. code-block here work on VSCode

    ```py
    channel: pycord.Channel = await find(pycord.Channel, id=1234567890)
    await channel.send('Hello, world!')
    ```

    .. code-block:: python3

        channel: pycord.Channel = await find(pycord.Channel, id=1234567890)
        await channel.send('Hello, world!')

    Returns
    -------
    A single non-Type variant of T in `cls`.
    """

    if not hasattr(cls, 'fetch') or not hasattr(cls, 'get'):
        raise RuntimeError('This class has no get or fetch function')

    mret = await cls.get(*args, **kwargs)

    if mret is None:
        return await cls.fetch(*args, **kwargs)
    else:
        return mret


# these two (@deprecated & @experimental) are mostly added for the future
def deprecated(alternative: str | None = None, removal: str | None = None):
    """
    Used to show that a provided API is in its deprecation period.

    Parameters
    ----------
    alternative: :class:`str` | None
        An optional alternative to use instead of this.
    removal: :class:`str`
        Planned removal version.
    """

    def wrapper(func: Callable):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            message = f'{func.__name__} has been deprecated.'

            if alternative:
                message += f' You can use {alternative} instead.'

            if removal:
                message += f' This feature will be removed by version {removal}.'

            warnings.warn(message, DeprecationWarning, 3)
            return func(*args, **kwargs)

        return decorator

    return wrapper


def experimental():
    """
    Used for showing that a provided API is still experimental.
    """

    def wrapper(func: Callable):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            message = f'{func.__name__} is an experimental feature, it may be removed at any time and breaking changes can happen without warning.'

            warnings.warn(message, DeprecationWarning, 3)
            return func(*args, **kwargs)

        return decorator

    return wrapper


def find_mimetype(data: bytes):
    """
    Gets the mimetype of the given bytes.

    Exceptions
    ----------
    ValueError: :class:`ValueError`
        The image mime type is not supported
    """

    if data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        return 'image/png'
    elif data[0:3] == b'\xff\xd8\xff' or data[6:10] in (b'JFIF', b'Exif'):
        return 'image/jpeg'
    elif data.startswith((b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61')):
        return 'image/gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'image/webp'
    else:
        raise ValueError('Unsupported image mime type given')


def to_datauri(f: File) -> str:
    """
    Turns a file into a data uri string.

    Parameters
    ----------
    f: :class:`.File`
        The file to turn into a data uri format.

    Returns
    -------
    :class:`str`
    """
    b = f.file.read()

    m = find_mimetype(b)

    b64 = base64.b64encode(b)

    return f'data:{m};base64,{b64}'
