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
from typing import Any

from aiohttp import ClientResponse

from .utils import parse_errors


class PycordException(Exception):
    pass


class BotException(PycordException):
    pass


class InteractionException(BotException):
    pass


class GatewayException(PycordException):
    pass


class NoIdentifiesLeft(GatewayException):
    pass


class DisallowedIntents(GatewayException):
    pass


class ShardingRequired(GatewayException):
    pass


class InvalidAuth(GatewayException):
    pass


class HTTPException(PycordException):
    def __init__(self, resp: ClientResponse, data: dict[str, Any] | None) -> None:
        self._response = resp
        self.status = resp.status

        if data:
            self.code = data.get('code', 0)
            self.error_message = data.get('message', '')

            if errors := data.get('errors'):
                self.errors = parse_errors(errors)
                message = self.error_message + '\n'.join(
                    f'In {key}: {err}' for key, err in self.errors.items()
                )
            else:
                message = self.error_message

        super().__init__(f'{resp.status} {resp.reason} (code: {self.code}): {message}')


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class InternalError(HTTPException):
    pass


class OverfilledShardsException(BotException):
    pass


class FlagException(BotException):
    pass


class ComponentException(BotException):
    pass
