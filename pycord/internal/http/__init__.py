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
from pycord.errors import Forbidden, HTTPException, NotFound, Unauthorized
from pycord.file import File
from pycord.internal.blocks import Block
from pycord.internal.http.audit_logs import AuditLogRoutes
from pycord.internal.http.auto_moderation import AutoModerationRoutes
from pycord.internal.http.channel import ChannelRoutes
from pycord.internal.http.emoji import EmojiRoutes
from pycord.internal.http.guild import GuildRoutes
from pycord.internal.http.guild_scheduled_event import GuildScheduledEventRoutes
from pycord.internal.http.guild_template import GuildTemplateRoutes
from pycord.internal.http.invite import InviteRoutes
from pycord.internal.http.route import Route, Route
from pycord.internal.http.stage_instance import StageInstanceRoutes
from pycord.internal.http.sticker import StickerRoutes
from pycord.internal.http.user import UserRoutes
from pycord.internal.http.voice import VoiceRoutes
from pycord.internal.http.webhook import WebhookRoutes

_log: logging.Logger = logging.getLogger(__name__)


class HTTPClient(
    AuditLogRoutes,
    AutoModerationRoutes,
    ChannelRoutes,
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
        data: dict[str, Any] | list[str | int | dict[str, Any]] | FormData | None = None,
        *,
        files: list[File] | None = None,
        reason: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | list[dict[str, Any]] | str | None:  # type: ignore
        endpoint = route.merge(self.url)

        if not self._session:
            await self.create()

        headers = self._headers.copy()
        if reason:
            headers['X-Audit-Log-Reason'] = reason

        if data:
            if isinstance(data, dict | list):
                data = utils.dumps(data)
                headers.update({'Content-Type': 'application/json'})

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

                response = await self._session.request(
                    method=method,
                    url=endpoint,
                    data=data,
                    headers=headers,
                    **kwargs,
                )

                response_data = await utils._text_or_json(response)
                _log.debug(f'Received {response_data} from request to {endpoint} ({response.status})')

                # ratelimited
                if response.status == 429:
                    try:
                        bucket = response.headers['X-RateLimit-Bucket']
                    except KeyError:
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
                            reset_after=float(response.headers['X-RateLimit-Reset-After']),
                            bucket=bucket,
                            globalrt=response.headers['X-RateLimit-Scope'] == 'global',
                        )

                        del self._blockers[bucket]
                        continue

                # something went wrong
                if response.status >= 400:
                    if response.status == 401:
                        raise Unauthorized(response, response_data)
                    elif response.status == 403:
                        raise Forbidden(response, response_data)
                    elif response.status == 404:
                        raise NotFound(response, response_data)
                    else:
                        raise HTTPException(response, response_data)

                return response_data
            print("Exceeded retries")
            raise ValueError
        finally:
            if files:
                for f in files:
                    f.close()

    def _prepare_message_form(self, files: list[File], payload: dict[str, Any] = None) -> FormData:
        if payload is None:
            payload = {}
        form = []
        attachments = []

        for index, file in enumerate(files):
            attachments.append({'id': index, 'filename': file.filename, 'description': file.description})
            form.append(
                {
                    'name': f'files[{index}]',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )

        payload['attachments'] = attachments
        form.insert(0, {'name': 'payload_json', 'content_type': 'application/json', 'value': utils.dumps(payload)})
        form_data = FormData(quote_fields=False)
        for f in form:
            form_data.add_field(**f)

        return form_data

    async def get_cdn_asset(self, url: str) -> bytes | None:
        async with self._session.get(url) as response:
            match response.status:
                case 200:
                    return await response.read()
                case 403:
                    raise Forbidden(response, None)
                case 404:
                    raise NotFound(response, None)
                case _:
                    raise HTTPException(response, None)
