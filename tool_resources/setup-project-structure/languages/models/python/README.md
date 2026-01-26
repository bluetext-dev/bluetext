# Python Models

Python implementations of entities, types, and operations.

## Structure

```
models/python/
├── pyproject.toml
├── README.md
└── models/           # The importable package
    ├── entities/     # Data structures with CRUD (backed by datastore)
    ├── types/        # Ephemeral data types (not persisted)
    └── operations/   # Public business logic functions
```

## Usage

```python
from models.entities.users import User, UserData
from models.types.auth import SignupRequest
from models.operations.users import signup, get_user
```

## Entities

Entities extend a base client class that provides CRUD:

```python
# models/python/models/entities/users.py
from pydantic import BaseModel
from clients.couchbase import BaseModelCouchbase

class UserData(BaseModel):
    name: str
    email: str
    role: str = "member"

class User(BaseModelCouchbase[UserData]):
    _collection_name = "users"
```

## Types

Types are ephemeral data structures (not persisted):

```python
# models/python/models/types/auth.py
from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
```

## Operations

Operations are the public API that services call:

```python
# models/python/models/operations/users.py
from models.entities.users import User, UserData
from models.types.auth import SignupRequest

def signup(request: SignupRequest) -> User:
    user = User(data=UserData(name=request.name, email=request.email))
    user.save()
    return user
```

## Architecture

```
Services → Operations → Entities → Clients → Datastore
              ↑
            Types (for request/response schemas)
```

Services call operations. Operations use entity CRUD. Entities extend client base classes.
