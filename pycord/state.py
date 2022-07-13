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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, Type, Union


if TYPE_CHECKING:
    from pycord.bot import Bot
    from pycord.rest import RESTApp


class AsyncDict(dict):
    """
    A dict with async methods to help support async dbs.
    """

    async def get(self, key: Any) -> Any:
        return super().get(key)

    async def pop(self, key: Any, default: Any | None = None) -> Any:
        return super().pop(key, default)

    async def values(self) -> list[Mapping[Any, Any]]:
        return super().values()  # type: ignore


@dataclass
class ConnectionState:
    _app: Union["RESTApp", "Bot"]
    """
    The app controlling the ConnectionState.
    """

    cache_timeout: int = 10000
    """
    Cache timeout in seconds.
    """

    store: Type[AsyncDict] = AsyncDict

    gateway_enabled: bool = False
    """
    Specifies if this ConnectionState is being controlled by a member which has Gateway Access.
    """

    async def start_cache(self) -> None:

        # channel_id: list of message objects
        self.messages: AsyncDict = self.store()

        # guild_id: guild object
        self.guilds: AsyncDict = self.store()

        # channel_id: channel object
        self.channels: AsyncDict = self.store()

        # guild_id: list of member objects.
        self.members: AsyncDict = self.store()
