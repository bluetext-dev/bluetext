# Entities

Data structures that define the shape of your data.

## Purpose

Entities are pure data definitions. They should not contain business logic or side effects.

## Example

```python
# models/python/entities/user.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
```

## Guidelines

1. **Use dataclasses**: Prefer `@dataclass` for simple, typed data structures
2. **No side effects**: Entities should not import clients or perform I/O
3. **Type everything**: Use type hints for all fields
4. **Keep it simple**: Entities are data, not behavior

## Visibility

Entities in this directory are public and can be imported by services. For internal-only entities, use `private/entities/`.
