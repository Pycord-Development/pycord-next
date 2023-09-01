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

import logging
import sys
from typing import TYPE_CHECKING, Any, Type, TypeVar, cast

import aiohttp
from aiohttp import BasicAuth, ClientSession, FormData, __version__ as aiohttp_version
from discord_typings.resources.application import ApplicationData
from discord_typings.resources.audit_log import AuditLogData, AuditLogEvents
from msgspec import json

from .._about import __version__
from ..errors import BotException, DiscordException, Forbidden, HTTPException, NotFound
from ..file import File
from ..missing import MISSING, Maybe
from ..utils import form_qs

_log = logging.getLogger(__name__)


T = TypeVar("T")


class Route:
    def __init__(
        self,
        client: "HTTPClient",
        path: str,
        guild_id: int | None = None,
        channel_id: int | None = None,
        webhook_id: int | None = None,
        webhook_token: str | None = None,
        **parameters: object,
    ) -> None:
        self.path: str = path.format(**parameters)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.webhook_id = webhook_id
        self.webhook_token = webhook_token
        self.parameters = parameters

    @property
    def bucket(self) -> str:
        return f"{self.path}:{self.guild_id}:{self.channel_id}:{self.webhook_id}:{self.webhook_token}"


class HTTPClient:
    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://discord.com/api/v10",
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self.base_url = base_url
        self._proxy = proxy
        self._proxy_auth = proxy_auth
        self._headers = {
            "User-Agent": "DiscordBot (https://pycord.dev, {0}) Python/{1[0]}.{1[1]} aiohttp/{2}".format(
                __version__, sys.version_info, aiohttp_version
            ),
        }
        if token:
            self._headers["Authorization"] = f"Bot {token}"

        self._session: None | ClientSession = None

    async def request(  # type: ignore[return]
        self,
        method: str,
        route: Route,
        data: dict[str, Any] | None = None,
        files: list[File] | None = None,
        form: list[dict[str, Any]] | None = None,
        *,
        reason: str | None = None,
        query_params: dict[str, str] | None = None,
        t: Type[T],
    ) -> T:
        endpoint = route.path

        if self._session is None:
            self._session = aiohttp.ClientSession(self.base_url)

        if TYPE_CHECKING:
            assert self._session

        headers = self._headers.copy()

        if reason:
            headers["X-Audit-Log-Reason"] = reason

        payload: bytes | FormData

        if data:
            payload = json.encode(data)
            headers.update({"Content-Type": "application/json"})

        if form and data:
            form.append({"name": "payload_json", "value": data})

        if files:
            if not form:
                form = []

            for idx, file in enumerate(files):
                form.append(
                    {
                        "name": f"files[{idx}]",
                        "value": file.file.read(),
                        "filename": file.filename,
                        "content_type": "application/octet-stream",
                    }
                )

        _log.debug(f"Requesting to {endpoint} with {data}, {headers}")

        for try_ in range(5):
            if files:
                for file in files:
                    file.reset(try_)

            if form:
                payload = FormData(quote_fields=False)
                for params in form:
                    payload.add_field(**params)

            r = await self._session.request(
                method,
                endpoint,
                data=data,
                headers=headers,
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
                params=query_params,
            )
            _log.debug(f"Received back {await r.text()}")

            if t:
                d = cast(T, json.decode(await r.read()))
            else:
                d = cast(T, await r.text())

            if r.status == 429:
                # TODO: properly handle rate limits
                _log.debug(f"Request to {endpoint} failed: Request returned rate limit")
                raise BotException("Rate Limit response received")

            elif r.status == 403:
                raise Forbidden(r, d)
            elif r.status == 404:
                raise NotFound(r, d)
            elif r.status == 500:
                raise DiscordException(r, d)
            elif r.ok:
                return d
            else:
                raise HTTPException(r, d)

    # audit log

    async def get_guild_audit_log(
        self,
        guild_id: int,
        user_id: Maybe[int] = MISSING,
        action_type: Maybe[AuditLogEvents] = MISSING,
        before: Maybe[int] = MISSING,
        after: Maybe[int] = MISSING,
        limit: Maybe[int] = MISSING,
    ) -> AuditLogData:
        path = form_qs(
            "/guilds/{guild_id}/audit-logs",
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )

        return cast(
            AuditLogData,
            await self.request(
                "GET", Route(self, path, guild_id=guild_id), t=AuditLogData
            ),
        )

    # application

    async def get_current_application(self) -> ApplicationData:
        return cast(
            ApplicationData,
            await self.request(
                "GET", Route(self, "/applications/@me"), t=ApplicationData
            ),
        )

    # channel
