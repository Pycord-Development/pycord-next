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

import inspect
from typing import Any

from .types import AsyncFunc


class ArgumentParser:
    def __init__(self) -> None:
        pass

    def get_arg_defaults(self, fnc: AsyncFunc) -> dict[str, Any]:
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
