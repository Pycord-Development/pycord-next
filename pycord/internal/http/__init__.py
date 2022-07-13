"""
pycord.internal.http
~~~~~~~~~~~~~~~~~~~~
Pycord's Internal HTTP Routes.

:copyright: 2021-2022 VincentRPS
:license: MIT, see LICENSE for more details.
"""

import logging
from typing import Any

from aiohttp import ClientSession
from discord_typings import EmojiData, Snowflake
from discord_typings.resources.user import UserData

from pycord import __version__, utils
from pycord.errors import Forbidden, HTTPException, NotFound, Unauthorized
from pycord.internal.blocks import Block

_log: logging.Logger = logging.getLogger(__name__)


class Route:
    def __init__(
        self,
        path: str,
        guild_id: int | None = None,
        channel_id: int | None = None,
        webhook_id: Snowflake | None = None,
        webhook_token: str | None = None
    ):
        self.path = path
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.webhook_id = webhook_id
        self.webhook_token = webhook_token

    def merge(self, url: str):
        return url + self.path


class HTTPClient:
    def __init__(self, token: str, version: int, max_retries: int = 5):
        # pyright hates identifying this as clientsession when its not-
        # sadly, aiohttp errors a lot when not creating client sessions on an async environment.
        self._session: ClientSession = None  # type: ignore
        self._headers: dict[str, str] = {
            'Authorization': 'Bot ' + token,
            'User-Agent': f'DiscordBot (https://github.com/pycord/pycord-v3, {__version__})',
            'Content-Type': 'application/json',
        }
        self.version = version
        self._blockers: dict[str, Block] = {}
        self.max_retries = max_retries
        self.url = f'https://discord.com/api/v{self.version}'

    async def create(self):
        # TODO: add support for proxies
        self._session = ClientSession()

    async def request(self, method: str, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any] | str:  # type: ignore
        endpoint = self.url + endpoint

        if not self._session:
            await self.create()

        # we only get 5 tries
        for _ in range(self.max_retries):
            for blocker in self._blockers.values():
                if blocker.path == endpoint:
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
                data=data if data is None else utils.dumps(data),
                headers=self._headers,
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
                    block = Block(endpoint)
                    self._blockers[bucket] = block

                    _log.debug(f'Blocking request to bucket {block.path} after resource ratelimit.')
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

    async def get_me(self) -> UserData:
        return await self.request('GET', '/users/@me')  # type: ignore

    async def edit_me(self, username: str | None = None, avatar: str | None = None) -> UserData:
        data = {}

        if username:
            data['username'] = username

        if avatar:
            data['avatar'] = avatar

        return await self.request('PATCH', '/users/@me', data)  # type: ignore

    async def get_guild_emojis(self, guild_id: int) -> list[EmojiData]:
        return await self.request('GET', f'/guilds/{guild_id}/emojis')  # type: ignore

    async def get_guild_emoji(self, guild_id: int, emoji_id: int) -> EmojiData:
        return await self.request('GET', f'/guilds/{guild_id}/emojis/{emoji_id}')  # type: ignore

    async def create_guild_emoji(self, guild_id: int, emoji_id: int) -> EmojiData:  # type: ignore
        ...

    async def edit_guild_emoji(self, guild_id: int, emoji_id: int) -> EmojiData:  # type: ignore
        ...
