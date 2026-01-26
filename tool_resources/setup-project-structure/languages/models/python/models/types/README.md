# Types

Data structures that don't fit into entities or operations.

## What Goes Here

- **Entities** = Data in a datastore, uses a client, has CRUD
- **Operations** = Public functions called by services
- **Types** = Everything else

Examples of types:
- Standalone request/response schemas
- Shared data structures used across multiple entities
- Configuration objects
- Enums and constants

## Note on Co-location

Types related to a specific entity can live in the entity file itself - no need to separate them pedantically. Only put types here when they're standalone or shared across multiple modules.

## Example

```python
# models/python/models/types/auth.py
from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
```

## Usage

```python
from models.types.auth import SignupRequest, TokenResponse
```
