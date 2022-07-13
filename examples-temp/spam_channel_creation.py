import asyncio

from discord_typings import TextChannelData

import pycord
from pycord.internal import Route

app = pycord.RESTApp()

# please replace this
GUILD: int = 0


@app.listen('hook')
async def on_hook():
    ts = []

    for _ in range(30):
        ts.append(app.http.request('POST', Route('/guilds/{guild_id}/channels', guild_id=GUILD), {'name': 'ratelimit-go-brr', 'type': 0}))

    belts: list[TextChannelData] = await asyncio.gather(*ts)  # type: ignore
    ts.clear()

    for belt in belts:
        ts.append(app.http.request('DELETE', Route('/channels/{channel_id}', channel_id=belt['id'])))

    await asyncio.gather(*ts)


app.run('token')
