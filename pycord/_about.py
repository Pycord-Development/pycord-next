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

import logging
import typing

__title__: str = 'pycord'
__author__: str = 'Pycord Development'
__license__: str = 'MIT'
__copyright__: str = 'Copyright 2021-present Pycord Development'
__version__: str = '3.0.0'
__git_sha1__: str = 'HEAD'


class VersionInfo(typing.NamedTuple):
    major: str
    minor: str
    micro: str
    releaselevel: typing.Literal['alpha', 'beta', 'candidate', 'final']
    serial: int


version_info: VersionInfo = VersionInfo(
    major=3, minor=0, micro=0, releaselevel='alpha', serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__: list[str] = [
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
    '__version__',
    'VersionInfo',
    'version_info',
]
