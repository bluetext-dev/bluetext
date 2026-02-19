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
    return await signup(request)

@router.get("/users/{user_id}")
async def get_user_data(user_id: str) -> User:
    return await get_user(user_id)
```

**Routes call operations, not entity CRUD directly.**

## Setting Up Client Access

If your models use clients (e.g., Couchbase), configure environment variables:

1.  **Set values and secrets**:
    `set-values-and-secrets(...)` (if needed for custom secrets)

2.  **Add env vars to service**:
    `setup-service-for-client(service: "my-api", client: "couchbase-client")`

**Note**: These tools handle necessary runtime updates.

## Hot Reload

Changes are automatically applied. **Always check logs after changes:**
```
get-container-logs(container: "my-api", limit: 50)
```

## Adding Dependencies

Call the service-specific tool:
```
<api-name>-add-dependencies(packages: "package-name")
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

## Key Rules

1. **Routes call operations** - Don't call entity CRUD or clients directly
2. **Operations = business logic** - Validation, transformations, rules
3. **Entities = data + CRUD** - Extend client base classes
4. **Types = schemas** - Request/response data structures
5. **Clients = connections** - Database access, external APIs