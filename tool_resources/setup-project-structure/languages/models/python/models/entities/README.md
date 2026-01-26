# Entities

Data structures backed by a datastore, extending a base client class that provides CRUD.

## Example

```python
# models/python/models/entities/users.py
from pydantic import BaseModel
from clients.couchbase import BaseModelCouchbase
from typing import Optional
from datetime import datetime


class UserData(BaseModel):
    name: str
    email: str
    role: str = "member"
    avatar_url: Optional[str] = None
    created_at: str = ""

    def __init__(self, **data):
        if not data.get("created_at"):
            data["created_at"] = datetime.utcnow().isoformat()
        super().__init__(**data)


class User(BaseModelCouchbase[UserData]):
    _collection_name = "users"
```

## Structure

1. **Data class** - Pydantic `BaseModel` defining the fields
2. **Entity class** - Extends `BaseModelCouchbase[DataClass]` with collection name

The base class (`BaseModelCouchbase`) provides CRUD operations automatically.

## Usage

Entities are used by operations:

```python
# In operations
from models.entities.users import User, UserData

def create_user(name: str, email: str) -> User:
    user = User(data=UserData(name=name, email=email))
    user.save()
    return user
```

## Guidelines

1. **Extend the base client class**: CRUD is inherited, not written manually
2. **Use Pydantic for data**: Type safety and validation built-in
3. **Set `_collection_name`**: Maps entity to datastore collection/table
4. **Business logic in operations**: Entities are data + CRUD, nothing more
