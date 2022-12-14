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
"""Implementation of Discord's Snowflake ID"""

from datetime import datetime, timezone

from .utils import DISCORD_EPOCH


class Snowflake(int):
    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(
            ((self >> 22) + DISCORD_EPOCH) / 1000, tz=timezone.utc
        )

    @property
    def worker_id(self) -> int:
        return (self & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        return (self & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        return self & 0xFFF

    def __hash__(self) -> int:
        return self >> 22
