# Private Models

Internal models that should not be imported by services.

## Purpose

This directory contains helper functions, internal data transformations, and implementation details that are not part of the public API.

## Structure

```
private/
├── entities/     # Internal data structures
├── operations/   # Internal helper functions
└── README.md
```

## When to Use

- Helper functions used by multiple operations
- Internal data transformations
- Implementation details that may change

## Example

```python
# models/python/private/operations/validation.py
"""Internal validation helpers."""

import re

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))

def normalize_email(email: str) -> str:
    return email.lower().strip()
```

Then use in public operations:

```python
# models/python/operations/users.py
from models.python.private.operations.validation import is_valid_email
```

## Guidelines

1. **Not for services**: Services should never import from `private/`
2. **Internal API**: Can change without affecting services
3. **Shared helpers**: Use for code reused across operations
