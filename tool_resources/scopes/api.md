# API Development Guidelines

FastAPI service with hot reload. Uses the models/clients architecture for business logic and data access.

## Architecture

```
API Service (controller logic)
    │
    ▼
Models (business logic)
    │
    ▼
Clients (database/service connections)
```

**Keep the API thin**: Routes handle HTTP concerns. Business logic goes in models.

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
├── entities/         # Data structures
└── operations/       # Business functions

clients/python/
└── couchbase/        # Database client
```

## Using Models

Import operations in your routes:

```python
from fastapi import APIRouter
from models.python.operations.users import get_user, create_user
from models.python.entities.user import User

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user_route(user_id: str) -> User:
    return get_user(user_id)  # Business logic in models

@router.post("/users")
async def create_user_route(email: str, name: str) -> User:
    return create_user(email, name)  # Validation in models
```

**Never import clients directly in routes.** Use operations.

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
    from clients.python.couchbase import get_client

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

1. **Routes = controller logic only** - HTTP handling, no business logic
2. **Models = business logic** - Validation, transformations, rules
3. **Clients = connections** - Database access, external APIs
4. **Operations over CRUD** - Never call raw client methods in routes
5. **Document dependencies** - Operations should list which clients they need
