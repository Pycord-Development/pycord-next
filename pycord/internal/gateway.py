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
from typing import TYPE_CHECKING, Protocol

from aiohttp import BasicAuth
from discord_typings import GetGatewayBotData
from mypy_extensions import trait

from ..task_descheduler import tasks
from .reserver import Reserver
from .shard import Shard

if TYPE_CHECKING:
    from ..state.core import State


@trait
class GatewayProtocol:
    def __init__(self, state: State) -> None:
        ...

    async def start(self) -> None:
        ...

    async def get_guild_members(
        self,
        guild_id: int,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: list[int] = [],
        nonce: str | None = None,
    ) -> None:
        """Get members inside of a Guild.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild id of the members.
        query: :class:`str`
            The query to use. Defaults to an empty string, or all members.
        limit: :class:`int`
            Only return `limit` amount of members.
        presences: :class:`bool`
            Whether to return presences with the members.
        user_ids: list[:class:`int`]
            A list of users to return the member objects of.
        nonce: :class:`str`
            A custom nonce to replace Pycord's own unique nonce.
        """


class Gateway(GatewayProtocol):
    def __init__(
        self,
        state: State,
        version: int,
        proxy: str | None,
        proxy_auth: BasicAuth | None,
        # shards
        shard_ids: list[int],
        shard_total: int,
    ) -> None:
        self._state: "State" = state
        self.shards: list[Shard] = []
        self.shard_ids = shard_ids
        self.shard_total = shard_total
        self.version = version
        self.proxy = proxy
        self.proxy_auth = proxy_auth

    async def start(self, gateway_data: GetGatewayBotData) -> None:
        self._state.shard_rate_limit = Reserver(
            gateway_data["session_start_limit"]["max_concurrency"], 5
        )
        self._state.shard_rate_limit.current = gateway_data["session_start_limit"][
            "remaining"
        ]

        for shard_id in self.shard_ids:
            self.shards.append(
                Shard(
                    self._state,
                    shard_id,
                    self.shard_total,
                    version=self.version,
                    proxy=self.proxy,
                    proxy_auth=self.proxy_auth,
                )
            )

        for shard in self.shards:
            async with tasks() as tg:
                tg[asyncio.create_task(shard.connect())]

    async def get_guild_members(
        self,
        guild_id: int,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: list[int] = [],
        nonce: str | None = None,
    ) -> None:
        pass
