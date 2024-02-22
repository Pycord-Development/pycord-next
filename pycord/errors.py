# MIT License
#
# Copyright (c) 2023 Pycord
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
from typing import Any

from aiohttp import ClientResponse


class PycordException(Exception):
    """
    The base exception class for Pycord.

    All exceptions that Pycord raises are subclasses of this.
    """
    pass


class BotException(PycordException):
    """
    The base exception class for bot-related errors.
    """
    pass


# HTTP
def _flatten_errors(errors: dict[str, Any], key: str = "") -> dict[str, list[str]]:
    items = {}
    for subkey, value in errors.items():
        if subkey == "_errors":
            items[key] = [error["message"] for error in value]
            continue
        elif isinstance(value, dict):
            items.update(_flatten_errors(value, f"{key}.{subkey}" if key else subkey))
        else:
            items[f"{key}.{subkey}"] = value
    return items


class HTTPException(PycordException):
    """
    A generic exception for when an HTTP request fails.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request.
    status: :class:`int`
        The status code of the HTTP request.
    response_data: :class:`str` | :class:`dict[str, Any]` | None
        The data returned from the HTTP request.
    request_data: :class:`dict[str, Any]` | :class:`list[Any]` | :class:`bytes` | None
        The data that was sent in the HTTP request.
    errors: dict[:class:`str`, list[:class:`str`]] | None
        The errors that were returned from the HTTP request.
        Keys are the location of the error in request data,
        using dot notation, and values are lists of error messages.
    message: :class:`str` | None
        The main error text indicating what went wrong.
    code: :class:`int` | None
        The Discord-specific error code that was returned as a result
        of the request. See the `Discord API documentation
        <https://discord.com/developers/docs/topics/opcodes-and-status-codes#json-json-error-codes>`_
        for more info.
    """
    def __init__(
        self,
        response: ClientResponse,
        response_data: str | dict[str, Any] | bytes | None,
        request_data: dict[str, Any] | list[Any] | None,
    ) -> None:
        self.response: ClientResponse = response
        self.status: int = response.status
        self.response_data: str | dict[str, Any] | bytes | None = response_data
        self.request_data: dict[str, Any] | list[Any] | None = request_data
        self.errors: dict[str, list[str]] | None = _flatten_errors(response_data) if isinstance(response_data, dict) else None
        if isinstance(response_data, dict) and "message" in response_data:
            self.message: str | None = response_data["message"]
            self.code: int | None = response_data.get("code")
        else:
            self.message: str | None = response_data
            self.code: int | None = None
        help_text: str = self.message or ""
        for error, messages in self.errors.items():
            help_text += f"\nIn {error}: {', '.join(messages)}"
        errcode: str = f" (error code: {self.code})" if self.code else ""
        super().__init__(f"{self.status} {response.reason}{errcode} {help_text}")

    @property
    def problem_values(self) -> dict[str, Any]:
        problems = {}
        for error in self.errors.keys():
            path = error.split(".")
            current = self.request_data
            for key in path:
                if isinstance(current, list):
                    current = current[int(key)]
                elif isinstance(current, dict):
                    current = current[key]
            problems[error] = current
        return problems


class Forbidden(HTTPException):
    """
    Exception that is raised for when status code 403 occurs.

    This is a subclass of :exc:`HTTPException`.
    """


class NotFound(HTTPException):
    """
    Exception that is raised for when status code 404 occurs.

    This is a subclass of :exc:`HTTPException`.
    """


class DiscordException(HTTPException):
    """
    Exception that is raised for when status code in the 5xx range occurs.

    This is a subclass of :exc:`HTTPException`.
    """


# Gateway
class ShardingRequired(BotException):
    """
    Discord is requiring your bot to use sharding.

    For more information, see the
    `Discord API documentation <https://discord.com/developers/docs/topics/gateway#sharding>`_.

    This is a subclass of :exc:`BotException`.
    """
    pass


class InvalidAuth(BotException):
    """
    Your bot token is invalid.

    This is a subclass of :exc:`BotException`.
    """
    pass


class DisallowedIntents(BotException):
    """
    You are using privledged intents that you have not been approved for.

    For more information, see the
    `Discord API documentation <https://discord.com/developers/docs/topics/gateway#privileged-intents>`_.

    This is a subclass of :exc:`BotException`.
    """
    pass
