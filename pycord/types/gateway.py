# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
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
from typing import Any, TypeVar, Mapping, Generic, Literal

from typing_extensions import NotRequired, TypedDict

from .guild import UnavailableGuild
from .user import User

StrT = TypeVar("StrT", bound=str)
MappingT = TypeVar("MappingT", bound=Mapping[str, Any])


class _GatewayDispatchEvent(TypedDict, Generic[StrT, MappingT]):
    op: Literal[0]
    d: MappingT
    s: int
    t: StrT


GatewayDispatchEvent = _GatewayDispatchEvent[str, Mapping[str, Any]]


class GatewayReadyData(TypedDict):
    v: int
    user: User
    guilds: list[UnavailableGuild]
    session_id: str
    resume_gateway_url: str
    shard: NotRequired[tuple[int, int]]


GatewayReadyEvent = _GatewayDispatchEvent[Literal["READY"], GatewayReadyData]


class GatewayHelloData(TypedDict):
    heartbeat_interval: int


class GatewayHelloEvent(TypedDict):
    op: Literal[10]
    d: GatewayHelloData


GatewayEvent = GatewayDispatchEvent | GatewayReadyEvent | GatewayHelloEvent
