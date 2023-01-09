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
import logging
from types import SimpleNamespace
from typing import Any, Type

import aiohttp

from pycord import utils

from ..state.core import State
from .sock import NativeSocket


class ConnectionData(SimpleNamespace):
    guild_id: int
    user_id: int
    session_id: str
    token: str


_log = logging.getLogger(__name__)


class NativeGateway:
    """
    Implementation of the Gateway for Voice
    """

    def __init__(
        self,
        state: State,
        session: aiohttp.ClientSession,
        publish_frames: bool = False,
        socket_cls: Type[NativeSocket] = NativeSocket,
    ) -> None:
        self._state = state
        self._publish_frames = publish_frames
        self._socket = socket_cls()
        self._socket_cls = socket_cls
        self._session = session
        self._ws = None
        self._stop_conn: asyncio.Task[None] | None = None
        self._receive_task: asyncio.Task[None] | None = None
        self.url: str | None = None
        self._data: ConnectionData | None = None

    async def connect(self, ws_url: str, connection: ConnectionData) -> None:
        if not ws_url.startswith('wss://'):
            ws_url = 'wss://' + ws_url

        self.url = ws_url
        self._data = connection

        try:
            _log.debug(
                f'({connection.guild_id}:{connection.session_id}): connecting to Voice Gateway: {ws_url}'
            )
            self._ws = await self._session.ws_connect(ws_url)
            _log.debug(
                f'({connection.guild_id}:{connection.session_id}): connected to Voice Gateway'
            )
        except (aiohttp.ClientConnectionError, aiohttp.ClientConnectorError):
            _log.error(
                f'({connection.guild_id}:{connection.session_id}): failed to establish a connection with {ws_url}, retrying in 10 seconds'
            )
            await asyncio.sleep(10)
            await self.connect(ws_url, connection)
            return

        asyncio.create_task(self._receive)

    async def _receive(self) -> None:
        async for message in self._ws:
            if message.type == aiohttp.WSMsgType.CLOSED:
                break
            elif message.type == aiohttp.WSMsgType.TEXT:
                data: dict[str, Any] = utils.loads(message.data)

                op = data.get('op')
                d = data.get('d')

                if op == 2:
                    await self._socket.start(d)
                elif op == 3:
                    self._stop_conn.set_result(None)
                    self._stop_conn = asyncio.create_task(self._stopper)

    async def _stopper(self) -> None:
        _log.critical('heartbeat failed to be received, remaking websocket')
        await self._ws.close()
        await self._receive_task.set_result(None)

        self._stop_conn = None
        self._receive_task = None
        self._ws = None

        await self.connect(self.url, self._data)
