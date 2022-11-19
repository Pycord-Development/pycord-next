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
from typing import Optional

from pycord.types import Snowflake

__all__ = ['Route', 'BaseRoute']


class BaseRoute:
    guild_id = Optional[int]
    channel_id = Optional[int]
    webhook_id: int | None
    webhook_token: str | None

    def __init__(
        self,
        path: str,
        guild_id: Snowflake | None = None,
        channel_id: Snowflake | None = None,
        webhook_id: Snowflake | None = None,
        webhook_token: str | None = None,
        **parameters: str | int,
    ) -> None:
        ...

    def merge(self, url: str) -> str:
        pass


class Route(BaseRoute):
    def __init__(
        self,
        path: str,
        guild_id: Snowflake | None = None,
        channel_id: Snowflake | None = None,
        webhook_id: Snowflake | None = None,
        webhook_token: str | None = None,
        **parameters: str | int,
    ):
        self.path = path

        # major parameters
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.webhook_id = webhook_id
        self.webhook_token = webhook_token

        self.parameters = parameters

    def merge(self, url: str):
        return url + self.path.format(
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            webhook_id=self.webhook_id,
            webhook_token=self.webhook_token,
            **self.parameters,
        )

    def __eq__(self, route: 'Route') -> bool:
        return (
            route.channel_id == self.channel_id
            or route.guild_id == self.guild_id
            or route.webhook_id == self.webhook_id
            or route.webhook_token == self.webhook_token
        )
