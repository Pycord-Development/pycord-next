from pycord.ext import pager
from asyncio import run

paginator = pager.Paginator([pager.Page() for _ in range(20)])

async def main() -> None:
    for _ in range(20):
        print(next(paginator))

    for _ in range(19):
        print(await paginator.backward())

run(main())
