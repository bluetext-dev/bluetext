# Operations

Functions that perform business logic on entities.

## Purpose

Operations encapsulate business rules. They use clients to interact with external services and return entities. Services should call operations, not CRUD functions directly.

## Example

```python
# models/python/operations/users.py
"""
User operations.

Client dependencies:
- couchbase
"""
from typing import Optional
from clients.python.couchbase import get_collection
from models.python.entities.user import User

def get_user(user_id: str) -> Optional[User]:
    """Retrieve a user by ID."""
    collection = get_collection("users")
    try:
        doc = collection.get(user_id)
        return User(**doc.content_as[dict])
    except DocumentNotFoundException:
        return None

def create_user(email: str, name: str) -> User:
    """Create a new user with validation."""
    # Business logic: validate email format, check uniqueness, etc.
    if not is_valid_email(email):
        raise ValueError("Invalid email format")

    user = User(
        id=generate_id(),
        email=email,
        name=name,
        created_at=datetime.utcnow()
    )

    collection = get_collection("users")
    collection.insert(user.id, asdict(user))
    return user
```

## Guidelines

1. **Document dependencies**: List client dependencies in the module docstring
2. **Return entities**: Operations should return entity types, not raw dicts
3. **Encapsulate logic**: Validation, transformations, and rules belong here
4. **No HTTP concerns**: Operations don't know about requests/responses

## Client Dependencies

When an operation uses a client, the service importing it needs the corresponding environment variables. Document dependencies clearly:

```python
"""
Client dependencies:
- couchbase: COUCHBASE_CONNECTION_STRING, COUCHBASE_USERNAME, ...
- temporal: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, ...
"""
```

## Visibility

Operations in this directory are public. For internal helpers, use `private/operations/`.
