Mirex
---

Distributed Redis based caching for discord bots.

---

### Basic example

```python
from redis import asyncio as aioredis

from mirex import Mirex

redis = aioredis.from_url("...")
mirex: Mirex = Mirex(redis)
```