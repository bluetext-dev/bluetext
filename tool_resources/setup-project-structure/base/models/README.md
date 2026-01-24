# Models

Models contain the data structures and business logic of the system. They serve as the central layer between services and clients.

## Purpose

Models centralize business logic so it can be shared across services. Services should focus on controller logic (routing, authentication, request handling) while models handle the actual work.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Services   │ ──▶ │    Models    │ ──▶ │   Clients    │
│  (controller │     │  (business   │     │  (external   │
│    logic)    │     │    logic)    │     │   services)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Structure

```
models/
├── python/
│   ├── entities/       # Data structures (public)
│   ├── operations/     # Business logic functions (public)
│   └── private/        # Internal models, not exported
│       ├── entities/
│       └── operations/
├── typescript/
│   ├── entities/
│   ├── operations/
│   └── private/
└── README.md
```

## Entities vs Operations

### Entities
Data structures that define the shape of your data. Entities are typically public and shared across the system.

```python
# models/python/entities/user.py
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str
```

### Operations
Functions that perform business logic. Operations use clients to interact with external services and return entities.

```python
# models/python/operations/users.py
from clients.python.couchbase import get_bucket
from models.python.entities.user import User

def get_user(user_id: str) -> User:
    bucket = get_bucket()
    doc = bucket.get(f"user:{user_id}")
    return User(**doc.content)

def create_user(email: str, name: str) -> User:
    # Business logic here, not in the service
    ...
```

**Important**: Services should call operations, not CRUD functions directly. Operations encapsulate business rules.

## Private Models

The `private/` directory contains models that are internal to the library and should not be imported by services. Use this for:
- Helper functions
- Internal data transformations
- Implementation details

## Client Dependencies

Models that use clients inherit their environment variable requirements. Document which clients a model depends on:

```python
# models/python/operations/users.py
"""
User operations.

Client dependencies:
- couchbase: COUCHBASE_CONNECTION_STRING, COUCHBASE_USERNAME, etc.
"""
```

When a service imports a model, it must have the required environment variables configured. Use `setup-service-for-client` to add them.

## Adding Models

Use the `add-entity` tool to scaffold new entities:

```bash
polytope run add-entity --client couchbase --language python --entity-singular user --entity-plural users
```

See the language-specific README in `models/<language>/` for more details.
