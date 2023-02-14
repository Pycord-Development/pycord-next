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
from __future__ import annotations

import asyncio
import logging
import zlib
from platform import system
from random import random
from typing import TYPE_CHECKING, Any

from aiohttp import (
    ClientConnectionError,
    ClientConnectorError,
    ClientSession,
    ClientWebSocketResponse,
    WSMsgType,
)

from ..errors import DisallowedIntents, InvalidAuth, ShardingRequired
from ..utils import dumps, loads
from .passthrough import PassThrough

if TYPE_CHECKING:
    from ..state import State
    from .notifier import Notifier

ZLIB_SUFFIX = b'\x00\x00\xff\xff'
url = '{base}/?v={version}&encoding=json&compress=zlib-stream'
_log = logging.getLogger(__name__)


RESUMABLE: list[int] = [
    4000,
    4001,
    4002,
    4003,
    4005,
    4007,
    4008,
    4009,
]


class Shard:
    def __init__(
        self,
        id: int,
        state: State,
        session: ClientSession,
        notifier: Notifier,
        version: int = 10,
    ) -> None:
        self.id = id
        self.session_id: str | None = None
        self.version = version
        self._token: str | None = None
        # while the rate limit normally is 120, it'd be nice to leave out
        # 10 for heartbeating
        self._rate_limiter = PassThrough(110, 60)
        self._notifier = notifier
        self._state = state
        self._session = session
        # I am not sure whether this is meant to be used, but it's the only thing
        # which can be "properly" typed upon
        self._inflator: zlib._Decompress | None = None  # type: ignore
        self._sequence: int | None = None
        self._ws: ClientWebSocketResponse | None = None
        self._resume_gateway_url: str | None = None
        self._heartbeat_interval: float | None = None
        self._hb_received: asyncio.Future[None] | None = None
        self._receive_task: asyncio.Task[None] | None = None
        self._connection_alive: asyncio.Future[None] = asyncio.Future()
        self._hello_received: asyncio.Future[None] | None = None
        self._hb_task: asyncio.Task[None] | None = None

    async def connect(self, token: str | None = None, resume: bool = False) -> None:
        self._hello_received = asyncio.Future()
        self._inflator = zlib.decompressobj()

        try:
            async with self._state.shard_concurrency:  # type: ignore
                _log.debug(f'shard:{self.id}: connecting to gateway')
                self._ws = await self._session.ws_connect(  # type: ignore
                    url=url.format(version=self.version, base=self._resume_gateway_url)
                    if resume and self._resume_gateway_url
                    else url.format(
                        version=self.version, base='wss://gateway.discord.gg'
                    ),
                    proxy=self._notifier.manager.proxy,
                    proxy_auth=self._notifier.manager.proxy_auth,
                )
                _log.debug(f'shard:{self.id}: connected to gateway')
        except (ClientConnectionError, ClientConnectorError):
            _log.debug(
                f'shard:{self.id}: failed to connect to discord due to connection errors, retrying in 10 seconds'
            )
            await asyncio.sleep(10)
            await self.connect(token=token, resume=resume)
            return
        else:
            self._receive_task = asyncio.create_task(self._recv())

            if token:
                await self._hello_received
                self._token = token
                if resume:
                    await self.send_resume()
                else:
                    await self.send_identify()

    async def send(self, data: dict[str, Any]) -> None:
        async with self._rate_limiter:
            d = dumps(data)
            _log.debug(f'shard:{self.id}: sending {d}')
            await self._ws.send_str(d)  # type: ignore

    async def send_identify(self) -> None:
        await self.send(
            {
                'op': 2,
                'd': {
                    'token': self._token,
                    'properties': {
                        'os': system(),
                        'browser': 'pycord',
                        'device': 'pycord',
                    },
                    'compress': True,
                    'large_threshold': self._state.large_threshold,
                    'shard': [self.id, self._notifier.manager.amount],
                    'intents': self._state.intents.as_bit,
                },
            }
        )

    async def send_resume(self) -> None:
        await self.send(
            {
                'op': 6,
                'd': {
                    'token': self._token,
                    'session_id': self.session_id,
                    'seq': self._sequence,
                },
            }
        )

    async def send_heartbeat(self, jitter: bool = False) -> None:
        if jitter:
            await asyncio.sleep(self._heartbeat_interval * random())  # type: ignore
        else:
            await asyncio.sleep(self._heartbeat_interval)  # type: ignore
        self._hb_received = asyncio.Future()
        _log.debug(f'shard:{self.id}: sending heartbeat')
        try:
            await self._ws.send_str(dumps({'op': 1, 'd': self._sequence}))  # type: ignore
        except ConnectionResetError:
            _log.debug(
                f'shard:{self.id}: failed to send heartbeat due to connection reset, reconnecting...'
            )
            self._receive_task.cancel()  # type: ignore
            if not self._ws.closed:  # type: ignore
                await self._ws.close(code=1008)  # type: ignore
            await self.connect(self._token, bool(self._resume_gateway_url))
            return
        try:
            await asyncio.wait_for(self._hb_received, 5)
        except asyncio.TimeoutError:
            _log.debug(f'shard:{self.id}: heartbeat waiting timed out, reconnecting...')
            self._receive_task.cancel()  # type: ignore
            if not self._ws.closed:  # type: ignore
                await self._ws.close(code=1008)  # type: ignore
            await self.connect(self._token, bool(self._resume_gateway_url))

    async def _recv(self) -> None:
        async for msg in self._ws:  # type: ignore
            if msg.type == WSMsgType.CLOSED:  # type: ignore
                break
            elif msg.type == WSMsgType.BINARY:  # type: ignore
                if len(msg.data) < 4 or msg.data[-4:] != ZLIB_SUFFIX:  # type: ignore
                    continue

                try:
                    text_coded = self._inflator.decompress(msg.data).decode('utf-8')  # type: ignore
                except Exception as e:
                    # while being an edge case, the data could sometimes be corrupted.
                    _log.debug(
                        f'shard:{self.id}: failed to decompress gateway data {msg.data}:{e}'  # type: ignore
                    )
                    continue

                _log.debug(f'shard:{self.id}: received message {text_coded}')

                data: dict[str, Any] = loads(text_coded)

                self._sequence = data.get('s')

                op: int = data.get('op')  # type: ignore
                d: dict[str, Any] | int | None = data.get('d')
                t: str | None = data.get('t')

                if op == 0:
                    if t == 'READY':
                        self.session_id = d['session_id']  # type: ignore
                        self._resume_gateway_url = d['resume_gateway_url']  # type: ignore
                        self._state.raw_user = d['user']  # type: ignore
                    asyncio.create_task(self._state.event_manager.publish(t, d))  # type: ignore
                elif op == 1:
                    await self._ws.send_str(dumps({'op': 1, 'd': self._sequence}))  # type: ignore
                elif op == 10:
                    self._heartbeat_interval = d['heartbeat_interval'] / 1000  # type: ignore

                    asyncio.create_task(self.send_heartbeat(jitter=True))
                    self._hello_received.set_result(True)  # type: ignore
                elif op == 11:
                    if not self._hb_received.done():  # type: ignore
                        self._hb_received.set_result(None)  # type: ignore

                        self._hb_task = asyncio.create_task(self.send_heartbeat())
                elif op == 7:
                    await self._ws.close(code=1002)  # type: ignore
                    await self.connect(token=self._token, resume=True)
                    return
                elif op == 9:
                    await self._ws.close()  # type: ignore
                    await self.connect(token=self._token)
                    return
        await self.handle_close(self._ws.close_code)  # type: ignore

    async def handle_close(self, code: int) -> None:
        _log.debug(f'shard:{self.id}: closed with code {code}')
        if self._hb_task and not self._hb_task.done():
            self._hb_task.cancel()
        if code in RESUMABLE:
            await self.connect(self._token, True)
        else:
            if code == 4004:
                raise InvalidAuth('Authentication used in gateway is invalid')
            elif code == 4011:
                raise ShardingRequired('Discord is requiring you shard your bot')
            elif code == 4014:
                raise DisallowedIntents(
                    "You aren't allowed to carry a privileged intent wanted"
                )

            if code > 4000 or code == 4000:
                await self._notifier.shard_died(self)
            else:
                # the connection most likely died
                await self.connect(self._token, resume=True)
