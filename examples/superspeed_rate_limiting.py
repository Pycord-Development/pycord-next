import asyncio
import logging
from typing import Any

import pycord

logging.basicConfig(level=logging.DEBUG)
api = pycord.HTTPClient('token')
GUILD_ID = 0


async def spam_channels() -> None:
    channels: list[dict[str, Any]] = []

    tasks: list[asyncio.Task] = [
        api.request('POST', pycord.Route('/guilds/{guild_id}/channels', guild_id=GUILD_ID), {'name': 'rate-limit-test'})
        for _ in range(50)
    ]

    channels = await asyncio.gather(*tasks)
    tasks.clear()

    tasks.extend(
        api.request('DELETE', pycord.Route('/channels/{channel_id}', channel_id=channel['id'])) for channel in channels
    )

    await asyncio.gather(*tasks)
    await api.close_session()


asyncio.run(spam_channels())
