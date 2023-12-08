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

from __future__ import annotations

import asyncio
import logging
import zlib
from asyncio import Task
from platform import system
from random import random
from typing import TYPE_CHECKING, Any

from aiohttp import BasicAuth, ClientConnectionError, ClientConnectorError, WSMsgType

from ..errors import DisallowedIntents, InvalidAuth, ShardingRequired
from ..task_descheduler import tasks
from ..utils import dumps, loads
from .reserver import Reserver

if TYPE_CHECKING:
    from ..state.core import State

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
    URL_FMT = "{base}/?v={version}&encoding=json&compress=zlib-stream"
    ZLIB_SUFFIX = b"\x00\x00\xff\xff"

    def __init__(
        self,
        state: State,
        shard_id: int,
        shard_total: int,
        version: int,
        proxy: str | None,
        proxy_auth: BasicAuth | None,
    ) -> None:
        self._state = state
        self.version = version
        self.shard_id = shard_id
        self.shard_total = shard_total

        # While Discord's rate limit is actually 120,
        # leaving out 10 gives Shards more safety in terms
        # of heart beating
        self.rate_limiter = Reserver(110, 60)
        self.open = False

        self._hb_task: Task | None = None
        self._recv_task: Task | None = None
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._hello_received = asyncio.Event()
        self._resume_gateway_url = None

    def log(self, level: int, msg: str) -> None:
        _log.log(level, f"shard:{self.shard_id}: {msg}")

    async def connect(self, resume: bool = False) -> None:
        self.open = False
        self._hello_received.clear()
        self._inflator = zlib.decompressobj()
        self._hb_task: Task | None = None
        self._recv_task: Task | None = None

        if not resume:
            self.session_id = None
            self._sequence = 0
            self._resume_gateway_url = None

        try:
            async with self._state.shard_rate_limit:
                self.log(logging.INFO, "attempting connection to gateway")
                self._ws = await self._state.http._session.ws_connect(
                    url=self.URL_FMT.format(
                        version=self.version, base=self._resume_gateway_url
                    )
                    if resume and self._resume_gateway_url
                    else self.URL_FMT.format(
                        version=self.version, base="wss://gateway.discord.gg"
                    ),
                    proxy=self._proxy,
                    proxy_auth=self._proxy_auth,
                )
        except (ClientConnectionError, ClientConnectorError):
            self.log(
                logging.ERROR,
                "connection errors led to failure in connecting to the gateway, trying again in 10 seconds",
            )
            await asyncio.sleep(10)
            await self.connect(resume=resume)
            return
        else:
            self.log(logging.INFO, "attempt successful")
            self.open = True

            self._recv_task = asyncio.create_task(self._recv())

            if not resume:
                await self._hello_received.wait()
                await self.send_identify()
            else:
                await self.send_resume()

    async def _recv(self) -> None:
        async for message in self._ws:
            if message.type == WSMsgType.CLOSED:
                break
            elif message.type == WSMsgType.BINARY:
                if len(message.data) < 4 or message.data[-4:] != self.ZLIB_SUFFIX:
                    continue

                try:
                    text_coded = self._inflator.decompress(message.data).decode("utf-8")
                except Exception as e:
                    # while being an edge case, the data could sometimes be corrupted.
                    self.log(
                        logging.ERROR,
                        f"failed to decompress gateway data {message.data}:{e}",
                    )
                    continue

                self.log(logging.DEBUG, f"received message {text_coded}")

                data: dict[str, Any] = loads(text_coded)

                self._sequence = data.get("s")

                async with tasks() as tg:
                    tg[asyncio.create_task(self.on_receive(data))]

        self.handle_close(self._ws.close_code)

    async def on_receive(self, data: dict[str, Any]) -> None:
        op: int = data.get("op")
        d: dict[str, Any] | int | None = data.get("d")
        t: str | None = data.get("t")

        if op == 0:
            if t == "READY":
                self.session_id = d["session_id"]
                self._resume_gateway_url = d["resume_gateway_url"]
                await self._state.cache["users"].upsert(d["user"]["id"], d["user"])
                self._state.user_id = d["user"]["id"]
            await self._state.event_manager.push(t, d)
        elif op == 1:
            await self._ws.send_str(dumps({"op": 1, "d": self._sequence}))
        elif op == 7:
            await self._ws.close(code=1002)
            await self.connect(resume=True)
            return
        elif op == 10:
            self._heartbeat_interval = d["heartbeat_interval"] / 1000

            self._hb_task = asyncio.create_task(self._heartbeat_loop())
            self._hello_received.set()

    async def _heartbeat_loop(self) -> None:
        jitter = True

        while not self._ws.closed:
            if jitter:
                jitter = False
                await asyncio.sleep(self._heartbeat_interval + random())
            else:
                await asyncio.sleep(self._heartbeat_interval)

            self.log(logging.DEBUG, "attempting heartbeat")

            try:
                await self._ws.send_str(dumps({"op": 1, "d": self._sequence}))
            except ConnectionResetError:
                self.log(
                    logging.ERROR,
                    f"failed to send heartbeat due to connection reset, attempting reconnection",
                )
                self._receive_task.cancel()
                if not self._ws.closed:
                    await self._ws.close(code=1008)
                await self.connect(bool(self._resume_gateway_url))
                return

    async def send(self, data: dict[str, Any]) -> None:
        async with self.rate_limiter:
            d = dumps(data)
            self.log(logging.DEBUG, f"sending {d}")
            await self._ws.send_str(d)

    async def send_identify(self) -> None:
        self.log(logging.INFO, "shard is identifying")

        await self.send(
            {
                "op": 2,
                "d": {
                    "token": self._state._token,
                    "properties": {
                        "os": system(),
                        "browser": "pycord",
                        "device": "pycord",
                    },
                    "compress": True,
                    "large_threshold": self._state.large_threshold,
                    "shard": [self.shard_id, self.shard_total],
                    "intents": self._state.intents,
                },
            }
        )

    async def send_resume(self) -> None:
        await self.send(
            {
                "op": 6,
                "d": {
                    "token": self._state._token,
                    "session_id": self.session_id,
                    "seq": self._sequence,
                },
            }
        )

    async def handle_close(self, code: int | None) -> None:
        self.log(logging.ERROR, f"shard socket closed with code {code}")
        if self._hb_task and not self._hb_task.done():
            self._hb_task.cancel()
        if code in RESUMABLE:
            await self.connect(True)
        elif code is None:
            await self.connect(True)
        else:
            if code == 4004:
                raise InvalidAuth("Authentication used in gateway is invalid")
            elif code == 4011:
                raise ShardingRequired("Discord is requiring you shard your bot")
            elif code == 4014:
                raise DisallowedIntents(
                    "You aren't allowed to carry a privileged intent wanted"
                )

            if code > 4000 or code == 4000:
                await self.connect(resume=False)
            else:
                # the connection most likely died
                await self.connect(resume=True)
