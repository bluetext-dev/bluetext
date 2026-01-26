# Operations

Public business logic functions that services call. Operations use entities and their CRUD.

## Example

```python
# models/python/models/operations/users.py
from models.entities.users import User, UserData
from models.types.auth import SignupRequest

def signup(request: SignupRequest) -> User:
    """Create a new user from signup request."""
    # Business logic: validation, transformations, etc.
    if not is_valid_email(request.email):
        raise ValueError("Invalid email")

    user = User(data=UserData(
        name=request.name,
        email=request.email,
    ))
    user.save()
    return user

def get_user(user_id: str) -> User:
    """Get a user by ID."""
    return User.get(user_id)

def deactivate_user(user_id: str) -> User:
    """Deactivate a user account."""
    user = User.get(user_id)
    user.data.role = "deactivated"
    user.save()
    return user
```

## Purpose

Operations are the public API that services import. They:
- Encapsulate business rules and validation
- Use entity CRUD methods internally
- May combine multiple entities in a single operation
- Use types for request/response schemas

## Usage

Services import and call operations:

```python
# In a FastAPI route
from models.operations.users import signup, get_user
from models.types.auth import SignupRequest

@router.post("/signup")
async def signup_route(request: SignupRequest) -> User:
    return signup(request)
```

## Guidelines

1. **Operations are the public interface**: Services call operations, not entity CRUD directly
2. **Business logic here**: Validation, transformations, rules
3. **Use entities for data access**: Call entity CRUD methods
4. **Use types for schemas**: Request/response types come from `models.types`
