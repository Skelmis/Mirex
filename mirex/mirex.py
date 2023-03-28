import asyncio
import datetime

import orjson
from redis import asyncio as aioredis


class Mirex:
    def __init__(self, redis_instance: aioredis.Redis):
        self.is_consuming: bool = True
        self.queue: asyncio.Queue = asyncio.Queue()
        self.redis_instance: aioredis.Redis = redis_instance

    def add_to_cache(
        self,
        key: str,
        item: dict,
        ttl: datetime.timedelta | None,
    ) -> None:
        """Adds an item to the cache.

        Parameters
        ----------
        key: str
            The string key to store this under
        item: dict
            A dictionary to be cached
        ttl: datetime.timedelta | None
            How many seconds this item should live
            in the cache for before eviction.
        """
        ttl = ttl.total_seconds() if ttl is not None else None
        self.queue.put_nowait((key, orjson.dumps(item), ttl))

    async def get_from_cache(self, key: str) -> dict | None:
        """Fetch an item from cache if it exists.

        Parameters
        ----------
        key: str
            The key this item is
            stored in the cache under.

        Returns
        -------
        dict
            The dictionary of cached data if found
        """
        item = await self.redis_instance.get(key)
        if item:
            return orjson.loads(item.decode("utf-8"))

    async def consume_queue(self):
        while self.is_consuming:
            item: tuple[str, bytes, float | None] = await self.queue.get()
            if item[2] is not None:
                await self.redis_instance.set(item[0], item[1], ex=item[2])
            else:
                await self.redis_instance.set(item[0], item[1])
