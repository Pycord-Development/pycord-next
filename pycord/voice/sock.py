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
import socket
import struct
from typing import TYPE_CHECKING, TypedDict

from ..events.other import VoiceServerUpdate

from .opus import OpusEncoder

if TYPE_CHECKING:
    from .gateway import VoiceGateway


class SocketData(TypedDict):
    ssrc: int
    ip: str
    port: int
    modes: list[str]


_log = logging.getLogger(__name__)


# TODO: add Opus packet encoding and sending
class VoiceSocket:
    """
    Implementation of a Socket connection to receive and send Opus data
    """

    _DEFAULT_MODE = 'xsalsa20_poly1305_lite'
    _socket: socket.socket
    _nonce: int = 0
    _encoder: OpusEncoder

    def __init__(self) -> None:
        self._connected = False
        self._vss = asyncio.Event()
        self._vsts = asyncio.Event()

    async def update(self, data: VoiceServerUpdate) -> None:
        if not self._connected:
            self._vss.set()
            

    async def start(self, gateway: 'VoiceGateway', data: SocketData) -> None:
        self._gateway = gateway
        self._socket_data = data
        self._encoder = OpusEncoder()
        # stored loop for faster and higher availability
        self._loop = asyncio.get_running_loop()
        _log.debug('creating new voice socket')
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setblocking(False)

        self.ssrc = data['ssrc']
        self.port = data['port']
        self.voko_ip = data['ip']

        # form a new packet
        packet = bytearray(70)
        struct.pack_into('>H', packet, 0, 1)  # 1 = Send
        struct.pack_into('>H', packet, 2, 70)  # 70 = Length
        struct.pack_into('>I', packet, 4, self.ssrc)

        # send the packet to the struct
        _log.debug('sending initial message to voice socket')
        self._socket.sendto(packet, (self.voko_ip, self.port))

        # receive stuff from the socket asynchronously
        conn_resp = await self._loop.sock_recv(self._socket, 70)

        # unraveling the IP.
        # ascii starting at the first byte and ending at a null byte
        ip_start = 4
        ip_end = conn_resp.index(0, ip_start)
        self.ip = conn_resp[ip_start:ip_end].decode('ascii')
        _log.debug(f'received ip: {self.ip}')

        _log.debug(f'selecting voice socket mode: {self._DEFAULT_MODE}')
        await self._gateway.select(self.ip, self.port, self._DEFAULT_MODE)

        self._connected = True
