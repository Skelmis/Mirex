Mirex
---

Distributed Redis based caching for discord bots.

---

Mirex makes no guarantees that objects will be saved and restored field for field. The discord API is too unstable to provide correctness in all cases given how frequently fields are added, removed or changed. If you notice a change please open an issue or PR so it can be updated.

---

### Basic example

```python
from redis import asyncio as aioredis

from mirex import Mirex

redis = aioredis.from_url("...")
mirex: Mirex = Mirex(redis)
```