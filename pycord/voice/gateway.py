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

from ..enums import SpeakingMask
from ..gateway.passthrough import PassThrough
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
        self._rate_limiter = PassThrough(110, 60)
        self._nonce: int = 0
        # mapping ssrcs and their speaking statuses
        self.ssrc_map: dict[str, dict[str, Any]] = {}
        self.secret_key = None

    async def send(self, data: dict[str, Any]) -> None:
        async with self._rate_limiter:
            await self._ws.send_str(utils.dumps(data))

    async def speak(self, state: SpeakingMask) -> None:
        await self.send({'op': 5, 'd': {'speaking': int(state), 'delay': 0}})

    async def identify(self, conn: ConnectionData) -> None:
        await self.send(
            {
                'op': 0,
                'd': {
                    'server_id': conn.guild_id,
                    'user_id': conn.user_id,
                    'session_id': conn.session_id,
                    'token': conn.token,
                },
            }
        )

    async def select(self, ip: str, port: int, mode: str) -> None:
        await self.send(
            {
                'op': 1,
                'd': {
                    'protocol': 'udp',
                    'data': {'address': ip, 'port': port, 'mode': mode},
                },
            }
        )

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

        asyncio.create_task(self.identify(connection))
        asyncio.create_task(self._receive())

    async def _receive(self) -> None:
        async for message in self._ws:
            if message.type == aiohttp.WSMsgType.CLOSED:
                break
            elif message.type == aiohttp.WSMsgType.TEXT:
                data: dict[str, Any] = utils.loads(message.data)

                op = data.get('op')
                d = data.get('d')

                if op == 2:
                    await self._socket.start(self, d)
                elif op == 4:
                    self.secret_key = data['secret_key']
                elif op == 5:
                    try:
                        self.ssrc_map[d['ssrc']]['speaking'] = d['speaking']
                    except KeyError:
                        self.ssrc_map[d['ssrc']] = {
                            'user_id': int(d['user_id']),
                            'speaking': d['speaking'],
                        }
                elif op == 6:
                    self._stop_conn.set_result(None)
                    self._stop_conn = asyncio.create_task(self._stopper)
                elif op == 8:
                    self._heartbeat_interval: float | int = (
                        d['heartbeat_interval'] / 1000
                    )

    async def _stopper(self) -> None:
        await asyncio.sleep(self._heartbeat_interval + 5)
        _log.critical('heartbeat failed to be received, remaking websocket')
        await self._ws.close()
        await self._receive_task.set_result(None)

        self._stop_conn = None
        self._receive_task = None
        self._ws = None

        # TODO: implement resumes
        await self.connect(self.url, self._data)

    async def _repeat_heartbeat(self) -> None:
        await asyncio.sleep(self._heartbeat_interval)
        _log.debug('sending heartbeat to voice gateway')
        self._nonce += 1
        await self._ws.send_str(utils.dumps({'op': 3, 'd': self._nonce}))
        self._heartbeat_task = asyncio.create_task(self._repeat_heartbeat())
