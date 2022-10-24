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

import asyncio
import logging
from typing import Any, Callable, Coroutine, Type, TypedDict

from discord_typings import ChannelData
from pycord.channel import _create_channel, Channel
from pycord.guild import BaseEmoji, BaseGuild, BaseRole, Emoji, Guild, Role
from pycord.internal import EventDispatcher, HTTPClient, start_logging
from pycord.internal.events import BaseEventDispatcher
from pycord.state import BaseConnectionState, ConnectionState
from pycord.user import BaseCurrentUser, BaseUser, CurrentUser, User


def find_loop():
    try:
        return asyncio.get_running_loop()
    except:
        return asyncio.new_event_loop()


class Models(TypedDict):
    user: Type[BaseUser]
    current_user: Type[BaseCurrentUser]
    state: Type[BaseConnectionState]
    guild: Type[BaseGuild]
    role: Type[BaseRole]
    emoji: Type[BaseEmoji]
    event_dispatcher: Type[BaseEventDispatcher]


class BaseRESTApp:
    token: str | None
    cache_timeout: int
    _version: int
    _level: int
    dispatcher: BaseEventDispatcher
    models: Models

    def __init__(self, *, version: int = 10, level: int = logging.INFO, cache_timeout: int = 10000) -> None:
        pass

    async def start(self, token: str) -> None:
        pass

    async def close(self) -> None:
        pass

    async def edit(self, username: str | None = None, avatar: bytes | None = None):
        pass

    @property
    async def guilds(self) -> list[BaseGuild]:
        pass

    def listen(self, name: Any) -> None:
        pass


class RESTApp(BaseRESTApp):
    def __init__(self, *, version: int = 10, level: int = logging.INFO, cache_timeout: int = 10000) -> None:
        self.token: str | None = None
        self.cache_timeout = cache_timeout
        self._version = version
        self._level = level

        self.models: Models = {
            'user': User,
            'current_user': CurrentUser,
            'state': ConnectionState,
            'guild': Guild,
            'role': Role,
            'emoji': Emoji,
            'event_dispatcher': EventDispatcher,
        }
        self.dispatcher = self.models['event_dispatcher']()

    async def start(self, token: str):
        self.token = token
        start_logging(level=self._level)
        self._state = self.models['state'](self, self.cache_timeout)
        await self._state.start_cache()

        self.http = HTTPClient(self.token, self._version)
        user_data = await self.http.get_current_user()
        self.user = self.models['current_user'](user_data, self._state)
        self.dispatcher.dispatch('hook')

    async def close(self):
        await self.http._session.close()

    async def edit(self, username: str | None = None, avatar: bytes | None = None):
        return await self.user.edit(username=username, avatar=avatar)

    async def get_channel(self, channel_id) -> Channel:
        data: ChannelData = await self.http.get_channel(channel_id)
        return _create_channel(data, self._state)

    @property
    async def guilds(self):
        return self._state.guilds.values()

    def listen(self, name: Any):
        def inner(func: Callable | Coroutine):
            self.dispatcher.add_listener(name=name, function=func)

        return inner
