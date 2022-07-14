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

import logging
import os
import sys
from typing import Union

import colorlog
import colorlog.escape_codes

COLORLOG_FORMAT = '%(log_color)s%(bold)s%(levelname)s | %(asctime)s | %(name)s: %(thin)s%(message)s%(reset)s'
UNCOLORED_FORMAT = '%(levelname)s $(asctime)s %(name)s: %(message)s'


def color_is_supported() -> bool:
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    if sys.platform != 'win32':
        return is_a_tty

    return is_a_tty and (
        'ANSICON' in os.environ or 'WT_SESSION' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode'
    )


def start_logging(level: Union[None, str, int]):
    if color_is_supported():
        colorlog.basicConfig(level=level, format=COLORLOG_FORMAT, stream=sys.stderr)
    else:
        logging.basicConfig(level=level, format=UNCOLORED_FORMAT, stream=sys.stderr)

    logging.info('Thank you for beta testing Pycord v3!')


if __name__ == '__main__':
    start_logging(logging.DEBUG)
    logging.critical('g')
