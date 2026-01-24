# Python Clients

Python implementations of service clients.

## Usage

Import clients in your Python models:

```python
from clients.python.couchbase import get_bucket, get_collection
from clients.python.temporal import get_client
```

## Adding a Client

Use the `add-client` tool:

```bash
polytope run add-client --name redis --language python
```

## Environment Variables

Each client requires specific environment variables. The client should validate these on import and fail immediately if missing.

Example implementation pattern:

```python
# clients/python/redis/__init__.py
import os

REDIS_URL = os.environ.get("REDIS_URL")
if not REDIS_URL:
    raise EnvironmentError("REDIS_URL environment variable is required")

def get_client():
    import redis
    return redis.from_url(REDIS_URL)
```

## Available Clients

Clients are added as needed for your project. Common clients include:
- `couchbase` - Couchbase database
- `temporal` - Temporal workflow engine
- `postgres` - PostgreSQL database
