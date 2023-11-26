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


import asyncio
import logging
import zlib
from asyncio import Task
from platform import system
from typing import Any

from aiohttp import BasicAuth, ClientConnectionError, ClientConnectorError, WSMsgType

from ..state.core import State
from ..task_descheduler import tasks
from ..utils import dumps, loads
from .reserver import Reserver

_log = logging.getLogger()


class Shard:
    URL_FMT = "{base}/?v={version}&encoding=json&compress=zlib-stream"
    ZLIB_SUFFIX = b"\x00\x00\xff\xff"

    def __init__(
        self,
        state: State,
        shard_id: int,
        shard_total: int,
        version: int,
        proxy: str,
        proxy_auth: BasicAuth,
    ) -> None:
        self._state = state
        self.version = version
        self.shard_id = shard_id
        self.shard_total = shard_total

        # While Discord's rate limit is actually 120,
        # leaving out 10 gives Shards more safety in terms
        # of heart beating
        self.rate_limiter = Reserver(110, 60)

        self._hb_task: Task | None = None
        self._recv_task: Task | None = None
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._hello_received = asyncio.Event()

    def log(self, level: int, msg: str) -> None:
        _log.log(level, f"shard:{self.shard_id}: {msg}")

    async def connect(self, resume: bool = False) -> None:
        self._hello_received.clear()
        self._inflator = zlib.decompressobj()

        try:
            async with self._state.shard_rate_limit:
                self.log(logging.INFO, "attempting connection to gateway")
                self._ws = self._state.http._session.ws_connect(
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
                self.log(logging.INFO, "attempt successful")
        except (ClientConnectionError, ClientConnectorError):
            self.log(
                logging.ERROR,
                "connection errors led to failure in connecting to the gateway, trying again in 10 seconds",
            )
            await asyncio.sleep(10)
            await self.connect(resume=resume)
            return
        else:
            self._recv_task = asyncio.create_task(self._recv())

            if not resume:
                await self._hello_received.wait()
                await self.send_identify()
            else:
                await self.send_resume()

    async def recv(self) -> None:
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
                    _log.debug(
                        f"shard:{self.id}: failed to decompress gateway data {message.data}:{e}"
                    )
                    continue

                _log.debug(f"shard:{self.id}: received message {text_coded}")

                data: dict[str, Any] = loads(text_coded)

                self._sequence = data.get("s")

                async with tasks() as tg:
                    tg[asyncio.create_task(self.on_receive(data))]

    async def on_receive(self, data: dict[str, Any]) -> None:
        op: int = data.get("op")
        d: dict[str, Any] | int | None = data.get("d")
        t: str | None = data.get("t")

        if op == 0:
            if t == "READY":
                self.session_id = d["session_id"]
                self._resume_gateway_url = d["resume_gateway_url"]
                self._state.cache["users"].upsert(d["user"]["id"], d["user"])
            self._state.event_manager.push("ready", d)
        elif op == 1:
            await self._ws.send_str(dumps({"op": 1, "d": self._sequence}))

    async def send(self, data: dict[str, Any]) -> None:
        async with self.rate_limiter:
            d = dumps(data)
            _log.debug(f"shard:{self.id}: sending {d}")
            await self._ws.send_str(d)

    async def send_identify(self) -> None:
        await self.send(
            {
                "op": 2,
                "d": {
                    "token": self._token,
                    "properties": {
                        "os": system(),
                        "browser": "pycord",
                        "device": "pycord",
                    },
                    "compress": True,
                    "large_threshold": self._state.large_threshold,
                    "shard": [self.id, self.shard_total],
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
