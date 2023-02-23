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


import asyncio
from io import BytesIO
import pathlib
from typing import BinaryIO, Protocol


def _open_file(path: pathlib.Path) -> BinaryIO:
    return path.expanduser().open('rb')


class File(Protocol):
    path: pathlib.Path | None
    filename: str
    file: BinaryIO
    spoiler: bool

    def reset(self, seek: int | bool = True) -> None:
        ...

    def close(self) -> None:
        ...


class SysFile(File):
    def __init__(
        self, path: str, filename: str | None = None, spoiler: bool = False
    ) -> None:
        self.path = pathlib.Path(path)
        self.filename = filename
        # assumes the event loop has already started
        self.spoiler = spoiler
        asyncio.create_task(self._hook_file())

    async def _hook_file(self) -> None:
        loop = asyncio.get_running_loop()

        self.file = await loop.run_in_executor(None, _open_file, _open_file, self._path)

        # assure we have control over closures
        self._closer = self.file.close
        self.file.close = lambda: None

        if self.filename is None:
            self.filename = self.path.name

        if self.spoiler and not self.filename.startswith('SPOILER_'):
            self.filename = f'SPOILER_{self.filename}'

        self._original_position = self.file.tell()

    def reset(self, seek: int | bool = True) -> None:
        if seek:
            self.file.seek(self._original_position)

    def close(self) -> None:
        self.file.close = self._closer
        self._closer()


class BytesFile(File):
    def __init__(self, filename: str, io: bytes | BytesIO) -> None:
        self.filename = filename
        self.file = BytesIO(io)

        # assure we have control over closures
        self._closer = self.file.close
        self.file.close = lambda: None

        if self.spoiler and not self.filename.startswith('SPOILER_'):
            self.filename = f'SPOILER_{self.filename}'

        self._original_position = self.file.tell()

    def reset(self, seek: int | bool = True) -> None:
        if seek:
            self.file.seek(self._original_position)

    def close(self) -> None:
        self.file.close = self._closer
        self._closer()
