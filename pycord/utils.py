# Copyright (c) 2021-2022 VincentRPS
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

try:
    import orjson

    HAS_ORJSON = True
except (ImportError, ModuleNotFoundError):
    import json

    HAS_ORJSON = False

from base64 import b64encode
from datetime import datetime, timezone
from typing import Any, Tuple

from aiohttp import ClientResponse

EPOCH = 1420070400000


async def _text_or_json(rp: ClientResponse):
    if rp.content_type == 'application/json':
        return await rp.json(loads=loads, encoding='utf-8')
    return await rp.text(encoding='utf-8')


def dumps(obj: Any) -> str:
    if HAS_ORJSON:
        return orjson.dumps(obj).decode('utf-8')
    else:
        return json.dumps(obj)


def loads(obj: str | bytes) -> Any:
    if HAS_ORJSON:
        return orjson.loads(obj)
    else:
        return json.loads(obj)


def grab_creation_time(id: int) -> datetime:
    ts = ((id >> 22) + EPOCH) / 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _get_image_mime_type(data: bytes):
    if data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        return 'image/png'
    elif data[0:3] == b'\xff\xd8\xff' or data[6:10] in (b'JFIF', b'Exif'):
        return 'image/jpeg'
    elif data.startswith((b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61')):
        return 'image/gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'image/webp'
    else:
        raise ValueError('Image type given is unsupported by discord')


def _convert_base64_from_bytes(data: bytes) -> str:
    fmt = 'data:{mime};base64,{data}'
    mime = _get_image_mime_type(data)
    b64 = b64encode(data).decode('ascii')
    return fmt.format(mime=mime, data=b64)


def _validate_image_params(key: str, fmt: str, size: int) -> Tuple[str, int]:
    # format validation

    static_formats = frozenset(("png", "jpg", "jpeg", "webp"))
    asset_formats = static_formats | {"gif"}

    animated = key.startswith("a_")
    if animated:
        fmt = fmt if fmt in asset_formats else "gif"
    else:
        fmt = fmt if fmt in static_formats else "png"

    # size validation

    # size must be between 16 and 4096 (2**4 and 2**12)
    if not 16 <= size <= 4096:
        size = max(min(4096, size), 16)
    # size must be a power of 2
    elif size & (size - 1) != 0:
        size = 1 << ((size - 1).bit_length())

    return fmt, size
