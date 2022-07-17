"""
pycord.internal.http
~~~~~~~~~~~~~~~~~~~~
Pycord's Internal HTTP Routes.

:copyright: 2021-2022 VincentRPS
:license: MIT, see LICENSE for more details.
"""

import logging
from typing import Any

from aiohttp import ClientSession, FormData
from discord_typings.resources.user import UserData

from pycord import __version__, utils
from pycord.file import File
from pycord.errors import Forbidden, HTTPException, NotFound, Unauthorized
from pycord.internal.blocks import Block
from pycord.internal.http.route import Route

from pycord.internal.http.audit_logs import AuditLogRoutes
from pycord.internal.http.auto_moderation import AutoModerationRoutes
from pycord.internal.http.emoji import EmojiRoutes
from pycord.internal.http.guild import GuildRoutes
from pycord.internal.http.route import Route
from pycord.internal.http.guild_scheduled_event import GuildScheduledEventRoutes
from pycord.internal.http.guild_template import GuildTemplateRoutes
from pycord.internal.http.invite import InviteRoutes
from pycord.internal.http.stage_instance import StageInstanceRoutes
from pycord.internal.http.sticker import StickerRoutes
from pycord.internal.http.user import UserRoutes
from pycord.internal.http.voice import VoiceRoutes
from pycord.internal.http.webhook import WebhookRoutes

_log: logging.Logger = logging.getLogger(__name__)


class HTTPClient(
    AuditLogRoutes,
    AutoModerationRoutes,
    EmojiRoutes,
    GuildRoutes,
    GuildScheduledEventRoutes,
    GuildTemplateRoutes,
    InviteRoutes,
    StageInstanceRoutes,
    StickerRoutes,
    UserRoutes,
    VoiceRoutes,
    WebhookRoutes,
):
    def __init__(self, token: str, version: int, max_retries: int = 5):
        # pyright hates identifying this as clientsession when its not-
        # sadly, aiohttp errors a lot when not creating client sessions on an async environment.
        self._session: ClientSession = None  # type: ignore
        self._headers: dict[str, str] = {
            'Authorization': 'Bot ' + token,
            'User-Agent': f'DiscordBot (https://github.com/pycord/pycord-v3, {__version__})',
        }
        self.version = version
        self._blockers: dict[str, Block] = {}
        self.max_retries = max_retries
        self.url = f'https://discord.com/api/v{self.version}'

    async def create(self):
        # TODO: add support for proxies
        self._session = ClientSession()

    async def request(
        self,
        method: str,
        route: Route,
        data: dict[str, Any] | None = None,
        *,
        files: list[File] | None = None,
        reason: str = None,
        **kwargs: Any
    ) -> dict[str, Any] | list[dict[str, Any]] | str | None:  # type: ignore
        endpoint = route.merge(self.url)

        if not self._session:
            await self.create()

        headers = self._headers.copy()
        if reason:
            headers['X-Audit-Log-Reason'] = reason

        if files:
            data = self._prepare_form(files, data)
        elif data:
            data = utils.dumps(data)
            headers.update({"Content-Type": "application/json"})

        try:
            for retry in range(self.max_retries):
                if files:
                    for f in files:
                        f.reset(retry)

                for blocker in self._blockers.values():
                    if (
                        blocker.route.channel_id == route.channel_id
                        or blocker.route.guild_id == route.guild_id
                        or blocker.route.webhook_id == route.webhook_id
                        or blocker.route.webhook_token == route.webhook_token
                    ):
                        _log.debug(f'Blocking request to bucket {blocker.bucket_denom} prematurely.')
                        await blocker.wait()
                    elif blocker.route.path == endpoint:
                        _log.debug(f'Blocking request to bucket {blocker.bucket_denom} prematurely.')
                        await blocker.wait()
                        break
                    elif blocker.is_global:
                        _log.debug(f'Blocking request to {endpoint} due to global ratelimit.')
                        await blocker.wait()
                        break

                r = await self._session.request(
                    method=method,
                    url=endpoint,
                    data=data,
                    headers=headers,
                    **kwargs,
                )

                # ratelimited
                if r.status == 429:
                    try:
                        bucket = r.headers['X-RateLimit-Bucket']
                    except:
                        continue
                    # block request until ratelimit ends.
                    block = self._blockers.get(bucket)
                    if block:
                        await block.wait()
                        continue
                    else:
                        block = Block(route)
                        self._blockers[bucket] = block

                        _log.debug(f'Blocking request to bucket {endpoint} after resource ratelimit.')
                        await block.block(
                            reset_after=float(r.headers['X-RateLimit-Reset-After']),
                            bucket=bucket,
                            globalrt=r.headers['X-RateLimit-Scope'] == 'global',
                        )

                        del self._blockers[bucket]
                        continue

                # something went wrong
                if r.status >= 400:
                    if r.status == 401:
                        raise Unauthorized
                    elif r.status == 403:
                        raise Forbidden
                    elif r.status == 404:
                        raise NotFound
                    else:
                        raise HTTPException

                _log.debug(f'Received {await r.text()} from request to {endpoint}')

                return await utils._text_or_json(r)
        finally:
            if files:
                for f in files:
                    f.close()

    def _prepare_form(self, files: list[File], payload: dict[str, Any] = {}) -> FormData:
        form = []
        attachments = []

        for index, file in enumerate(files):
            attachments.append(
                {
                    "id": index,
                    "filename": file.filename,
                    "description": file.description
                }
            )
            form.append(
                {
                    "name": f"files[{index}]",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream"
                }
            )

        payload["attachments"] = attachments
        form.insert(0, {"name": "payload_json", "content_type": "application/json", "value": utils.dumps(payload)})
        form_data = FormData(quote_fields=False)
        for f in form:
            form_data.add_field(**f)

        return form_data

    # this should get moved to an asset-related http file
    async def get_cdn_asset(self, url: str) -> bytes:
        async with self._session.get(url) as response:
            match response.status:
                case 200:
                    return await response.read()
                case 403:
                    raise Forbidden
                case 404:
                    raise NotFound
                case _:
                    raise HTTPException

    async def get_me(self) -> UserData:
        return await self.request('GET', Route('/users/@me'))  # type: ignore

    async def edit_me(self, username: str | None = None, avatar: str | None = None) -> UserData:
        data = {}

        if username:
            data['username'] = username

        if avatar:
            data['avatar'] = avatar

        return await self.request('PATCH', Route('/users/@me'), data)  # type: ignore
