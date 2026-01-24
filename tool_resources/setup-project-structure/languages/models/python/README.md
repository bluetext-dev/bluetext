# Python Models

Python implementations of entities and operations.

## Structure

```
models/python/
├── entities/       # Data structures (public)
├── operations/     # Business logic functions (public)
├── private/        # Internal models, not exported
│   ├── entities/
│   └── operations/
└── README.md
```

## Usage

Import models in your Python services:

```python
from models.python.entities.user import User
from models.python.operations.users import get_user, create_user
```

## Adding Models

### Entities

Use the `add-entity` tool to scaffold new entities:

```bash
polytope run add-entity --client couchbase --language python --entity-singular user --entity-plural users
```

Or create manually in `entities/`:

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

Create operations in `operations/`:

```python
# models/python/operations/users.py
"""
User operations.

Client dependencies:
- couchbase
"""
from clients.python.couchbase import get_collection
from models.python.entities.user import User

def get_user(user_id: str) -> User:
    collection = get_collection("users")
    doc = collection.get(user_id)
    return User(**doc.content_as[dict])

def create_user(email: str, name: str) -> User:
    # Business logic here
    ...
```

## Client Dependencies

Document which clients your operations depend on. Services importing these operations need the corresponding environment variables configured.

See `operations/README.md` and `entities/README.md` for more details.
