# Python Clients

Python implementations of service clients.

## Structure

```
clients/python/
├── pyproject.toml
├── README.md
└── clients/           # The importable package
    ├── couchbase/     # Couchbase client (added via add-client)
    ├── temporal/      # Temporal client (added via add-client)
    └── ...
```

## Usage

Import clients in your Python models:

```python
from clients.couchbase import get_bucket, get_collection
from clients.temporal import get_client
```

The nested `clients/` directory is intentional - it allows the package at `clients/python` to expose `clients` as the importable package name.

## Adding a Client

Use the `add-client` tool:

```bash
polytope run add-client --name couchbase --language python
polytope run add-client --name temporal --language python
```

## Environment Variables

Each client requires specific environment variables. The client should validate these on import and fail immediately if missing.

Example implementation pattern:

```python
# clients/python/clients/redis/__init__.py
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
- `twilio` - Twilio SMS/communication
