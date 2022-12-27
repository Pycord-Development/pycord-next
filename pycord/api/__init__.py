"""
pycord.api
~~~~~~~~~~
Implementation of the Discord API.

:copyright: 2021-present Pycord Development
:license: MIT
"""

import logging
import sys
from typing import Any

from aiohttp import BasicAuth, ClientSession, __version__ as aiohttp_version

from .. import utils
from .._about import __version__
from ..errors import BotException, Forbidden, HTTPException, InternalError, NotFound
from ..utils import dumps
from .execution import Executer
from .json_decoder import JSONDecoder
from .route import BaseRoute, Route
from .routers import *

__all__ = ['Route', 'BaseRoute', 'HTTPClient']

_log = logging.getLogger(__name__)


class HTTPClient(ApplicationCommands, Messages):
    def __init__(
        self,
        token: str | None = None,
        base_url: str = 'https://discord.com/api/v10',
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
        verbose: bool = False,
    ) -> None:
        self.base_url = base_url
        self._json_decoder = JSONDecoder()
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._headers = {
            'User-Agent': 'DiscordBot (https://pycord.dev, {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'.format(
                __version__, sys.version_info, aiohttp_version
            ),
        }
        if token:
            self._headers['Authorization'] = f'Bot {token}'
        self.verbose = verbose

        self._session: None | ClientSession = None
        self._executers: list[Executer] = []

    async def create_session(self) -> None:
        self._session = ClientSession()

    async def close_session(self) -> None:
        await self._session.close()
        self._session = None

    async def request(
        self,
        method: str,
        route: BaseRoute,
        data: dict[str, Any] | None = None,
        *,
        reason: str | None = None,
        query_params: dict[str, str] | None = None,
    ) -> str | dict[str, Any] | bytes:
        endpoint = route.merge(self.base_url)

        if self._session is None:
            await self.create_session()

        headers = self._headers.copy()

        if reason:
            headers['X-Audit-Log-Reason'] = reason

        if data:
            # TODO: Support msgspec
            data: str = dumps(data=data)
            headers.update({'Content-Type': 'application/json'})

        _log.debug(f'Requesting to {endpoint} with {data}, {headers}')

        for executer in self._executers:
            if executer.is_global or executer.route == route:
                _log.debug(f'Pausing request to {endpoint}: Found rate limit executer')
                await executer.wait()

        for _ in range(5):
            r = await self._session.request(
                method,
                endpoint,
                data=data,
                headers=headers,
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
                params=query_params,
            )
            _log.debug(f'Received back {await r.text()}')

            data = await utils._text_or_json(cr=r, self=self)

            if r.status == 429:
                _log.debug(f'Request to {endpoint} failed: Request returned rate limit')
                executer = Executer(route=route)

                self._executers.append(executer)
                await executer.executed(
                    reset_after=data['retry_after'],
                    is_global=r.headers.get('X-RateLimit-Scope') == 'global',
                    limit=int(r.headers.get('X-RateLimit-Limit', 10)),
                )
                self._executers.remove(executer)
                continue

            elif r.status == 403:
                raise Forbidden(resp=r, data=data)
            elif r.status == 404:
                raise NotFound(resp=r, data=data)
            elif r.status == 500:
                raise InternalError(resp=r, data=data)
            elif r.ok:
                return data
            else:
                if self.verbose:
                    raise BotException(r, data)
                else:
                    raise HTTPException(resp=r, data=data)

    async def get_gateway_bot(self) -> dict[str, Any]:
        return await self.request('GET', Route('/gateway/bot'))
