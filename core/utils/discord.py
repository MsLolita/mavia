import asyncio
from typing import Optional

import discum


def _get_username(token: str, proxy: str):
    bot = discum.Client(token=token, proxy=proxy, log=False)

    for _ in range(3):
        resp = bot.info()
        if resp is not None:
            return resp.json().get("username")


async def get_username(token: str, proxy: Optional[str | None] = None):
    return await asyncio.to_thread(_get_username, token=token, proxy=proxy)

