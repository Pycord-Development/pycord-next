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
from datetime import datetime
import logging
import platform
import threading
import time
import zlib
from typing import TYPE_CHECKING, Any

from aiohttp import WSMsgType
from discord_typings.gateway import GatewayEvent

from pycord import utils

from ...errors import GatewayException
from ...state import ConnectionState
from ..events import EventDispatcher

if TYPE_CHECKING:
    from .manager import ShardManager

ZLIB_SUFFIX = b'\x00\x00\xff\xff'
url = 'wss://gateway.discord.gg/?v={version}&encoding=json&compress=zlib-stream'
_log = logging.getLogger(__name__)


# NOTE: This ramble is about using Thread's here instead of Task's, made by VincentRPS.
# the decision of using a thread instead of just using a perpetual task seems to be controversial to a lot of people
# I don't really care too much about that, everything here is thread safe and everything runs as fast and as well as
# if I implemented a more complex and memory intensive (most likely due to having a lot of tasks running) version
# with an asyncio.Task.
# NOTE: I have thought of using multiprocessing here but I'm pretty sure it would still block the main event loop
# since I use `while True`, which is obviously massively not ideal as everything uses the event loop.
class HeartThread(threading.Thread):
    def __init__(self, shard: "Shard", state: ConnectionState, interval: float, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.shard = shard
        self._state = state
        self._interval = interval
        self._sequence: int | None = None
        self.disconnected: bool = False
        self.daemon: bool = True
        self._loop = loop

    def run(self):
        while True:
            if not self.disconnected:
                time.sleep(self._interval)

                payload = {'op': 1, 'd': self._sequence}
                coroutine = self.shard.send(payload)
                future = asyncio.run_coroutine_threadsafe(coro=coroutine, loop=self._loop)
                future.result()


class Shard:
    def __init__(
        self,
        shard_id: int,
        shard_count: int,
        state: ConnectionState,
        events: EventDispatcher,
        manager: "ShardManager",
        version: int = 10,
        timeout: int = 30
    ) -> None:
        self.id = shard_id
        self.shard_count = shard_count
        self._events = events
        self.version = version
        self._state = state
        self.manager = manager
        self._session_id: str | None = None
        self.requests_this_minute: int = 0
        self._stop_clock: bool = False
        self._buf = bytearray()
        self._inf = zlib.decompressobj()
        self._ratelimit_lock: asyncio.Event | None = None
        self._rot_done: asyncio.Event = asyncio.Event()
        self.current_rotation_done: bool = False
        self._sequence: int | None = None  # type: ignore
        self._resumable: bool | None = None
        self._reconnectable: bool = True
        self._last_heartbeat_ack: datetime | None = None
        self._heartbeat_timeout = timeout

        self._receive_task: asyncio.Task | None = None
        self._clock_task: asyncio.Task | None = None

        if not self._state.gateway_enabled:
            raise GatewayException(
                'ConnectionState used is not gateway enabled. ' '(if you are using RESTApp, please move to Bot.)'
            )

    async def start_clock(self) -> None:
        try:
            self._rot_done.clear()
            await asyncio.sleep(60)
            self.requests_this_minute = 0

            if self._stop_clock:
                return

            self._rot_done.set()

            try:
                self._clock_task = asyncio.create_task(self.start_clock())
            except:
                # user has most likely exited this process.
                return
        except asyncio.CancelledError:
            pass

    async def send(self, data: dict[Any, Any]) -> None:
        if self.requests_this_minute == 119:
            if data.get('op') == 1:
                pass
            elif self._ratelimit_lock:
                await self._ratelimit_lock.wait()
            else:
                self._ratelimit_lock = asyncio.Event()
                await self._rot_done.wait()
                self._ratelimit_lock.set()
                self._ratelimit_lock: asyncio.Event | None = None

        _log.debug(f'shard:{self.id}:> {data}')

        payload = utils.dumps(data)
        payload = payload.encode('utf-8')  # type: ignore

        await self._ws.send_bytes(payload)

        self.requests_this_minute += 1

    async def connect(self, token: str) -> None:
        _log.debug(f'shard:{self.id}: Connecting to the Gateway.')
        self._ws = await self._state._app.http._session.ws_connect(url.format(version=self.version))

        self.token = token

        # There are some scenarios where the Gateway client cannot resume its previous session and
        # has to start all over again.
        if self._session_id is None or not self._resumable:
            if self._session_id is not None:
                _log.debug(f'shard:{self.id}:Reconnecting to Gateway')
            await self.identify()
            self._receive_task = asyncio.create_task(self.receive())
            self._clock_task = asyncio.create_task(self.start_clock())
        else:
            _log.debug(f'shard:{self.id}:Reconnecting to Gateway')
            await self.resume()
            self._receive_task = asyncio.create_task(self.receive())
            self._clock_task = asyncio.create_task(self.start_clock())

    async def disconnect(self, code: int = 1000, reconnect: bool = True) -> None:
        if not self._ws.closed and self.receive_task and self.clock_task:
            self._stop_clock = True
            self._reconnectable = reconnect
            await self._ws.close(code=code)

            for task in (self._receive_task, self._clock_task):
                task.cancel()
                await task

            self.manager.shard_disconnected_hook(self.id)

    async def receive(self) -> None:
        async for message in self._ws:
            try:
                if self._last_heartbeat_ack and (
                    datetime.now() - self._last_heartbeat_ack
                ).total_seconds() > self._heartbeat_timeout:
                    # zombified connection, reconnect
                    await self.disconnect(1008)

                if message.type == WSMsgType.BINARY:
                    if len(message.data) < 4 or message.data[-4:] != ZLIB_SUFFIX:
                        continue

                    self._buf.extend(message.data)

                    try:
                        encoded = self._inf.decompress(self._buf).decode('utf-8')
                    except:
                        # This data was most likely corrupted
                        self._buf = bytearray()  # clear buffer
                        continue

                    self._buf = bytearray()

                    data: GatewayEvent = utils.loads(encoded)

                    _log.debug(f'shard:{self.id}:< {encoded}')

                    self._sequence: int = data['s']

                    self._events.dispatch('WEBSOCKET_MESSAGE_RECEIVE', data)

                    op = data.get('op')
                    t = data.get('t')

                    if op == 0:
                        if t == 'READY':
                            _log.info(f'shard:{self.id}:Connected to Gateway')
                            self._events.dispatch('ready')
                            self._session_id = data['d']['session_id']
                    elif op == 7:
                        self._resumable = True
                        await self.disconnect()
                        break
                    elif op == 9:
                        self._resumable = data['d']
                        await self.disconnect()
                        break
                    elif op == 10:
                        interval = data['d']['heartbeat_interval'] / 1000
                        self._ratelimiter = HeartThread(self, self._state, interval, asyncio.get_running_loop())
                        await self.send({'op': 1, 'd': None})
                        self._ratelimiter.start()
                    elif op == 11:
                        self._last_heartbeat_ack = datetime.now() # no need for a timezone aware date, this is for this program only

                elif message.type == WSMsgType.CLOSED:
                    await self.disconnect(reconnect=False)
                    break
            except asyncio.CancelledError:
                break

    async def identify(self) -> None:
        await self.send(
            {
                'op': 2,
                'd': {
                    'token': self.token,
                    'intents': self._state._app.intents,  # type: ignore
                    'properties': {
                        'os': platform.system(),
                        'browser': 'pycord',
                        'device': 'pycord',
                    },
                    'shard': (self.id, self.shard_count),
                    'compress': True,
                },
            }
        )

    async def resume(self) -> None:
        await self.send(
            {
                'op': 6,
                'd': {
                    'token': self.token,
                    'session_id': self._session_id,
                    'seq': self._sequence,
                },
            }
        )
