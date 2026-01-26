# API Development Guidelines

FastAPI service with hot reload. Uses the models/clients architecture for business logic and data access.

## Architecture

```
API Routes → Operations → Entities → Clients → Datastore
                 ↑
               Types (for request/response schemas)
```

**Keep the API thin**: Routes handle HTTP concerns. Business logic goes in operations.

## Project Structure

```
services/my-api/
├── src/backend/
│   ├── routes/       # API endpoints (controller logic)
│   ├── conf.py       # Configuration
│   └── workflows/    # Temporal workflows (if used)
├── bin/              # Run scripts
└── polytope.yml      # Container config
```

Models and clients are shared at project level:
```
models/python/
└── models/
    ├── entities/     # Data structures with CRUD
    ├── types/        # Request/response schemas
    └── operations/   # Business logic (services call these)

clients/python/
└── clients/
    └── couchbase/    # Database client with base classes
```

## Using Models

Import operations in your routes:

```python
from fastapi import APIRouter
from models.operations.users import signup, get_user
from models.types.auth import SignupRequest
from models.entities.users import User

router = APIRouter()

@router.post("/signup")
async def signup_route(request: SignupRequest) -> User:
    return signup(request)  # Business logic in operations

@router.get("/users/{user_id}")
async def get_user_route(user_id: str) -> User:
    return get_user(user_id)
```

**Routes call operations, not entity CRUD directly.**

## Setting Up Client Access

If your models use clients (e.g., Couchbase), configure environment variables:

```bash
# 1. Set values and secrets
polytope run set-values-and-secrets --source couchbase-client

# 2. Add env vars to service
polytope run setup-service-for-client --service my-api --client couchbase-client

# 3. Restart to apply
pt run stack --mcp
```

## Hot Reload

Changes are automatically applied. **Always check logs after changes:**
```
get-container-logs(container: <api-name>, limit: 50)
```

Manual restart only needed when adding environment variables.

## Adding Dependencies

```
polytope run <api-name>-add --packages "package-name"
```

## Temporal Workflows

### Setup
1. Add Temporal Server: `add-and-run-service(template: "temporal", name: "temporal")`
2. Add Temporal client: `add-client(name: "temporal", language: "python")`
3. Configure env vars: `setup-service-for-client(service: "my-api", client: "temporal-client")`

### Best Practice: Import Inside Activities

```python
@activity.defn
def my_activity(input: MyInput) -> MyOutput:
    # CORRECT: Import inside activity
    from clients.couchbase import get_client

    client = get_client()
    return MyOutput(...)
```

## Authentication

1. Enable: `USE_AUTH = True` in `conf.py`
2. Configure JWT (JWK URL, audience)
3. Protect routes:

```python
from ..utils import RequestPrincipal

@router.get("/protected")
async def protected_route(principal: RequestPrincipal):
    return {"claims": principal.claims}
```

## Key Rules

1. **Routes call operations** - Never call entity CRUD or clients directly
2. **Operations = business logic** - Validation, transformations, rules
3. **Entities = data + CRUD** - Extend client base classes
4. **Types = schemas** - Request/response data structures
5. **Clients = connections** - Database access, external APIs
