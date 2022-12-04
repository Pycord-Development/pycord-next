"""
pycord.api
~~~~~~~~~~
Implementation of the Discord API.

:copyright: 2021-present VincentRPS
:license: MIT
"""
import logging
import sys
from typing import Any, Optional

from aiohttp import BasicAuth, ClientSession, __version__ as aiohttp_version

from pycord._about import __version__

from .. import utils
from ..errors import Forbidden, HTTPException, InternalError, NotFound
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
        token: str,
        base_url: str = 'https://discord.com/api/v10',
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.base_url = base_url
        self._json_decoder = JSONDecoder()
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._headers = {
            'Authorization': f'Bot {token}',
            'User-Agent': 'DiscordBot (https://pycord.dev, {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'.format(
                __version__, sys.version_info, aiohttp_version
            ),
        }

        self._session: None | ClientSession = None
        self._executers: list[Executer] = []

    async def create_session(self) -> None:
        self._session = ClientSession()

    async def close_session(self) -> None:
        if not self._session:
            return

        await self._session.close()
        self._session = None

    async def request(
        self,
        method: str,
        route: BaseRoute,
        data: Optional[dict[str, Any]] = None,
        *,
        reason: Optional[str] = None,
        query_params: Optional[dict[str, str]] = None,
    ) -> str | dict[str, Any] | bytes:
        endpoint = route.merge(self.base_url)

        if self._session is None:
            await self.create_session()

        session = cast(ClientSession, self._session)

        headers = self._headers.copy()

        if reason:
            headers['X-Audit-Log-Reason'] = reason

        _log.debug(f'Requesting to {endpoint} with {data}, {headers}')

        for executer in self._executers:
            if executer.is_global or executer.route == route:
                _log.debug(f'Pausing request to {endpoint}: Found rate limit executer')
                await executer.wait()

        for _ in range(5):
            r = await session.request(
                method,
                endpoint,
                json=data,
                headers=headers,
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
                params=query_params,
            )

            received_data: str | dict[str, Any] = await utils._text_or_json(cr=r, self=self)
            _log.debug(f'Received back {received_data}')

            if r.status == 429 and isinstance(received_data, dict):
                _log.debug(f'Request to {endpoint} failed: Request returned rate limit')
                executer = Executer(route=route)

                self._executers.append(executer)
                await executer.executed(
                    reset_after=received_data['retry_after'],
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
                return received_data
            else:
                raise HTTPException(resp=r, data=data)

        raise RuntimeError("Failed to make an HTTP request 5 times.")

    async def get_gateway_bot(self) -> dict[str, Any]:
        data = await self.request('GET', Route('/gateway/bot'))
        return cast(dict[str, Any], data)
