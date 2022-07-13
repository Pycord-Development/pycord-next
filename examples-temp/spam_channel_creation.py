import asyncio

from discord_typings import TextChannelData

import pycord

app = pycord.RESTApp()

# please replace this
GUILD: int = 0


@app.listen('hook')
async def on_hook():
    ts = []

    for _ in range(30):
        ts.append(app.http.request('POST', f'/guilds/{GUILD}/channels', {'name': 'ratelimit-go-brr', 'type': 0}))

    belts: list[TextChannelData] = await asyncio.gather(*ts)  # type: ignore
    ts.clear()

    for belt in belts:
        ts.append(app.http.request('DELETE', f'/channels/{belt["id"]}'))

    await asyncio.gather(*ts)


app.run('token')
