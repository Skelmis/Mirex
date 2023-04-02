import asyncio
import datetime
import logging
from typing import TypeVar, Type, Optional, Union, Any

import orjson
from redis import asyncio as aioredis

from mirex.serializers import guild_as_dict, role_as_dict, emoji_as_dict

T = TypeVar("T")
NS = TypeVar("NS")
log = logging.getLogger(__name__)


class Mirex:
    def __init__(self, *, redis_instance: aioredis.Redis, namespace, connection_state):
        self.is_consuming: bool = True
        self.queue: asyncio.Queue = asyncio.Queue()
        self.redis_instance: aioredis.Redis = redis_instance
        self._is_currently_consuming: bool = False
        self._state = connection_state
        self._namespace: NS = namespace
        self.mappings = {
            namespace.Guild: guild_as_dict,
            namespace.Role: role_as_dict,
            namespace.Emoji: emoji_as_dict,
        }

    def add_to_cache(
        self,
        item: Union[dict, Any],
        ttl: Optional[datetime.timedelta] = None,
    ) -> None:
        """Adds an item to the cache.

        Parameters
        ----------
        item: Union[dict, Any]
            The entry to be cached. This can either
            be the converted dictionary or class to convert.
        ttl: Optional[datetime.timedelta]
            How many seconds this item should live
            in the cache for before eviction.

        Raises
        ------
        ValueError
            The provided class instance doesn't have
            a conversion method yet
        """
        if not self._is_currently_consuming:
            log.critical(
                "Mirex is not consuming items from the queue yet,"
                " ensure consume_queue is running in a task."
            )

        key = f"{item.__class__.__name__.upper()}:{item.id}"
        if not isinstance(item, dict):
            try:
                item = self.mappings[type(item)](item)
            except KeyError:
                raise ValueError(
                    f"I do not yet know how to turn {item.__class__.__name__} into a dictionary"
                ) from None

        ttl = ttl.total_seconds() if ttl is not None else None
        self.queue.put_nowait((key, orjson.dumps(item), ttl))

    async def consume_queue(self):
        if self._is_currently_consuming:
            log.warning(
                "Looks like your trying to consume the "
                "queue concurrently when you only need to call this once"
            )

        self._is_currently_consuming = True
        while self.is_consuming:
            item: tuple[str, bytes, float | None] = await self.queue.get()
            if item[2] is not None:
                await self.redis_instance.set(item[0], item[1], ex=item[2])
            else:
                await self.redis_instance.set(item[0], item[1])

        self._is_currently_consuming = False

    async def aget_guild(self, guild_id: int) -> Optional[Any]:
        return await self.aget_class(f"GUILD:{guild_id}", self._namespace.Guild)

    async def aget_class(self, key, mapping: Type[T]) -> Optional[T]:
        raw_data = await self.redis_instance.get(key)
        if raw_data is None:
            return None

        # TODO Figure out how to handle classes
        #      that don't follow the below paradigm such as emoji
        raw_data = orjson.loads(raw_data.decode("utf-8"))
        return mapping(data=raw_data, state=self._state)
