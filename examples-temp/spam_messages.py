import asyncio

from discord_typings import MessageData

import pycord
from pycord.internal import Route

app = pycord.RESTApp()
CHANNEL_ID = 0

@app.listen('hook')
async def on_hook():
    ts = []

    for _ in range(10):
        ts.append(app.http.request('POST', Route('/channels/{channel_id}/messages', channel_id=CHANNEL_ID), {'content': 'ratelimit go brr'}))

    futs: list[MessageData] = await asyncio.gather(*ts)
    ts.clear()

    for future in futs:
        ts.append(app.http.request('DELETE', Route(f'/channels/{{channel_id}}/messages/{future["id"]}', channel_id=CHANNEL_ID)))

    await asyncio.gather(*ts)

loop = asyncio.new_event_loop()
loop.run_until_complete(app.start('token'))
loop.run_forever()
