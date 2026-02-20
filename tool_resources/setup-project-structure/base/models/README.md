# Models

Models contain the data structures and business logic of the system.

## Architecture

```
Services → Operations → Entities → Clients → Datastore
              ↑
            Types (for request/response schemas)
```

- **Services** call operations (never entities or clients directly)
- **Operations** contain business logic, use entity CRUD
- **Entities** extend client base classes, provide CRUD automatically
- **Types** are ephemeral data structures for requests/responses
- **Clients** handle datastore connections

## Structure

```
models/
├── python/
│   ├── pyproject.toml
│   └── models/           # The importable package
│       ├── entities/     # Data structures with CRUD (backed by datastore)
│       ├── types/        # Ephemeral data types (not persisted)
│       └── operations/   # Public business logic functions
└── README.md
```

## Entities

Entities extend a client base class that provides CRUD:

```python
from pydantic import BaseModel
from clients.couchbase import BaseModelCouchbase

class UserData(BaseModel):
    name: str
    email: str

class User(BaseModelCouchbase[UserData]):
    _collection_name = "users"
```

## Types

Ephemeral data structures (not persisted):

```python
from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
```

## Operations

Public business logic that services call:

```python
from models.entities.users import User, UserData
from models.types.auth import SignupRequest

def signup(request: SignupRequest) -> User:
    user = User(data=UserData(name=request.name, email=request.email))
    user.save()
    return user
```

## Usage

```python
from models.entities.users import User
from models.types.auth import SignupRequest
from models.operations.users import signup
```

## Resources

A **Resource** is the combination of an Entity + Types + Operations. It represents a complete data-backed concept with full CRUD business logic. Use `add-endpoint` with `layers: ["entity", "resource"]` to scaffold a resource without API routes:

```
add-endpoint(client: "couchbase", language: "python", entity-singular: "task", entity-plural: "tasks", fields: [{name: "title", type: "str"}, {name: "done", type: "bool"}], layers: ["entity", "resource"])
```

This generates:
- `models/python/models/entities/tasks.py` — Entity with fields and CRUD
- `models/python/models/types/tasks.py` — Create/Update request types
- `models/python/models/operations/tasks.py` — CRUD operations

## Adding Models

Use `add-endpoint` to scaffold a full endpoint (entity + types + operations + routes):
```
add-endpoint(client: "couchbase", language: "python", entity-singular: "task", entity-plural: "tasks", fields: [{name: "title", type: "str"}], service: "python-fast-api")
```

Or use `add-entity` to scaffold just the entity:
```
add-entity(client: "couchbase", language: "python", entity-singular: "user", entity-plural: "users", fields: [{name: "name", type: "str"}, {name: "email", type: "str"}])