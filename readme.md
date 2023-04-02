Mirex
---

Distributed Redis based caching for discord bots.

---

Mirex makes no guarantees that objects will be saved and restored field for field. The discord API is too unstable to provide correctness in all cases given how frequently fields are added, removed or changed. If you notice a change please open an issue or PR so it can be updated.

---

### Basic example

Given how early in development this library is, this is an extremely simple POC however it does work.

```python
import asyncio
import os

import disnake
from disnake.ext import commands
from redis import asyncio as aioredis

from mirex import Mirex

bot = commands.InteractionBot(intents=disnake.Intents.all())

redis = aioredis.from_url("redis://127.0.0.1:6379")
mirex = Mirex(
    namespace=disnake,
    redis_instance=redis,
    connection_state=bot._connection,
)


@bot.event
async def on_ready():
    asyncio.create_task(mirex.consume_queue())
    g = await bot.fetch_guild(...)
    mirex.add_to_cache(g)
    guild: disnake.Guild = await mirex.aget_guild(...)
    assert guild == g
    print("Done")


bot.run(os.environ["TOKEN"])
```