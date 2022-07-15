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
        ts.append(
            app.http.create_guild_channel(GUILD, name='ratelimit-go-brr', channel_type=0)
        )

    belts: list[TextChannelData] = await asyncio.gather(*ts)  # type: ignore
    ts.clear()

    for belt in belts:
        ts.append(app.http.request('DELETE', Route('/channels/{channel_id}', channel_id=belt['id'])))  # type: ignore

    await asyncio.gather(*ts)


app.run('token')
