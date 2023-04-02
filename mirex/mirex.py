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
        self._cache_queue: asyncio.Queue = asyncio.Queue()
        self._eviction_queue: asyncio.Queue = asyncio.Queue()
        self.redis_instance: aioredis.Redis = redis_instance
        self._is_currently_consuming: bool = False
        self._is_currently_evicting: bool = False
        self._state = connection_state
        self._namespace: NS = namespace
        self.mappings = {
            namespace.Guild: guild_as_dict,
            namespace.Role: role_as_dict,
            namespace.Emoji: emoji_as_dict,
        }

    def _preflight_checks(self):
        if not self._is_currently_consuming:
            log.critical(
                "Mirex is not consuming items from the queue yet,"
                " ensure consume_queue is running in a task."
            )

        if not self._is_currently_evicting:
            log.critical(
                "Mirex is not evicting items from the queue yet,"
                " ensure consume_eviction is running in a task."
            )

    def inject_hooks(self):
        """Inject Mirex into your discord
        library so the cache is automatically populated.

        This does remove your libraries built in caching
        so you will need to use Mirex for all cache hits after this call.
        """
        # guild lives primarily in state so this is fairly chill
        self._state._add_guild = self.add_to_cache

        # TODO This will leak as emojis and stickers
        #      need to be removed at the same time within this call
        self._state._remove_guild = self.remove_from_cache

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
        self._preflight_checks()
        key = f"{item.__class__.__name__.upper()}:{item.id}"
        if not isinstance(item, dict):
            try:
                item = self.mappings[type(item)](item)
            except KeyError:
                raise ValueError(
                    f"I do not yet know how to turn {item.__class__.__name__} into a dictionary"
                ) from None

        ttl = ttl.total_seconds() if ttl is not None else None
        self._cache_queue.put_nowait((key, orjson.dumps(item), ttl))

    def remove_from_cache(self, key: Union[str, Any]) -> None:
        """Evict something from the cache.

        Parameters
        ----------
        key: Union[str, Any]
            The key to remove from cache.

            Keys are structured as the class name
            in all capitals and the ID of the object
            seperated by a :

            For example "GUILD:808030843078836254"
        """
        self._preflight_checks()
        if not isinstance(key, str):
            # Make some educated guesses here
            key = f"{key.__class__.__name__.upper()}:{key.id}"

        self._eviction_queue.put_nowait(key)

    async def consume_queue(self):
        """Handle cache addition."""
        if self._is_currently_consuming:
            log.warning(
                "Looks like your trying to consume the "
                "queue concurrently when you only need to call this once"
            )

        self._is_currently_consuming = True
        while self.is_consuming:
            item: tuple[str, bytes, float | None] = await self._cache_queue.get()
            if item[2] is not None:
                await self.redis_instance.set(item[0], item[1], ex=item[2])  # noqa
            else:
                await self.redis_instance.set(item[0], item[1])  # noqa

        self._is_currently_consuming = False

    async def consume_eviction(self):
        """Handle cache eviction."""
        if self._is_currently_evicting:
            log.warning(
                "Looks like your trying to evict the "
                "queue concurrently when you only need to call this once"
            )

        self._is_currently_evicting = True
        while self.is_consuming:
            item: str = await self._eviction_queue.get()
            await self.redis_instance.delete(item)  # noqa

        self._is_currently_evicting = False

    async def aget_guild(self, guild_id: int) -> Optional[Any]:
        return await self.aget_class(f"GUILD:{guild_id}", self._namespace.Guild)

    async def aget_class(self, key, mapping: Type[T]) -> Optional[T]:
        self._preflight_checks()
        raw_data = await self.redis_instance.get(key)
        if raw_data is None:
            return None

        # TODO Figure out how to handle classes
        #      that don't follow the below paradigm such as Emoji
        raw_data = orjson.loads(raw_data.decode("utf-8"))
        return mapping(data=raw_data, state=self._state)
