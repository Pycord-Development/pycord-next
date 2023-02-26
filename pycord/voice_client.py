# cython: language_level=3
# Copyright (c) 2022-present Pycord Development
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
from typing import TYPE_CHECKING, Type

from .voice.gateway import ConnectionData

if TYPE_CHECKING:
    from .state.core import State

from .voice import VoiceGateway, VoiceSocket
from .gateway import ShardManager


class VoiceClient:
    def __init__(
        self,
        guild_id: int,
        channel_id: int,
        state: State,
        gateway: Type[VoiceGateway] = VoiceGateway,
        socket: Type[VoiceSocket] = VoiceSocket,
        send_packets_as_events: bool = False,
    ) -> None:
        self.guild_id = guild_id
        self.channel_id = channel_id
        self._state = state
        self._gateway_cls = gateway
        self._socket_cls = socket
        self._send_packets_as_events = send_packets_as_events

    async def connect(
        self, gateway: ShardManager, self_mute: bool = False, self_deaf: bool = False
    ) -> None:
        server_info = await gateway.update_voice_state(
            self.guild_id, self.channel_id, self_mute, self_deaf, True
        )

        self.gateway = self._gateway_cls(
            self._state, gateway.session, self._send_packets_as_events, self._socket_cls
        )
        await self.gateway.connect(
            server_info['endpoint'],
            ConnectionData(
                guild_id=server_info['guild_id'],
                session_id=server_info['sid'],
                user_id=int(self._state.user.id),
                token=server_info['token'],
            ),
        )


