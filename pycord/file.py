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

import os
import io
from typing import Union, Optional

__all__ = ("File",)

class File:
    """Represents a file that can be sent via Discord.

    Attributes:
        filename (str): 

    """
    fp: io.BufferedIOBase
    filename: str | None
    description: str | None
    spoiler: bool

    def __init__(
        self,
        fp: str | bytes | os.PathLike | io.BufferedIOBase,
        filename: str | None = None,
        *,
        description: str | None = None,
        spoiler: bool = False,
    ) -> None:
        if isinstance(fp, io.IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValueError(f"File buffer {fp!r} must be seekable and readable")
            self.fp = fp
            self._original_pos = fp.tell()
            self._owner = False
        else:
            self.fp = open(fp, "rb")
            self._original_pos = 0
            self._owner = True

        if filename is None:
            if isinstance(fp, str):
                _, filename = os.path.split(fp)
            else:
                filename = getattr(fp, "name", None)
 
        self.spoiler = False
        self.filename = filename
        if filename.startswith("SPOILER_"):
            self.spoiler = True
            self.filename = filename
        elif spoiler is True:
            self.spoiler = True
            self.filename = f"SPOILER_{filename}"

        self.description = description
        self._close = self.fp.close
        self.fp.close = lambda: None

    def reset(self, seek = True) -> None:
        # seek to initial position on failed requests
        # on the first try, `seek` will be 0, so the file
        # doesn't get reset
        if seek:
            self.fp.seek(self._original_pos)

    def close(self) -> None:
        # close stream that we opened
        self.fp.close = self._close
        if self._owner:
            self.fp.close()
