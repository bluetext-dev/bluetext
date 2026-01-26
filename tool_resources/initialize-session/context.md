# Bluetext Development Framework

## Architecture

```
Services → Operations → Entities → Clients → Datastore
               ↑
             Types
```

- **Services**: Frontends and APIs. Handle routing, auth, request/response.
- **Operations**: Public business logic that services call.
- **Entities**: Data structures with CRUD, extend client base classes.
- **Types**: Ephemeral data structures (requests, responses, etc.).
- **Clients**: Connections to external services (Couchbase, Temporal, etc.).

## Project Structure

```
project/
├── services/
│   ├── my-frontend/
│   └── my-api/
├── models/
│   └── python/
│       └── models/
│           ├── entities/     # Data + CRUD
│           ├── operations/   # Business logic
│           └── types/        # Ephemeral data
├── clients/
│   └── python/
│       └── clients/
│           └── couchbase/
└── config/
```

## Available Templates

### Services
- `api_python_fastapi` - Python FastAPI backend
- `frontend_typescript_react-router-v7` - React TypeScript frontend

### Infrastructure
- `couchbase-server_enterprise-v7` - Couchbase database
- `postgres` - PostgreSQL database
- `temporal` - Temporal workflow engine
- `temporal-ui` - Temporal web UI

### Clients
- `couchbase` - Couchbase database client
- `temporal` - Temporal workflow client

## Typical Workflow

### 1. Add Services
```
add-and-run-service(template: "api_python_fastapi", name: "api")
add-and-run-service(template: "frontend_typescript_react-router-v7", name: "frontend")
```

### 2. Add Client
Connect services to a datastore:
```
add-client(name: "couchbase", language: "python")
```

### 3. Configure Service for Client
```
setup-service-for-client(service: "api", client: "couchbase-client")
```

### 4. Add Entity
```
add-entity(client: "couchbase", language: "python", entity-singular: "user", entity-plural: "users")
```

### 5. Write Operations
Write operations that use the entity's CRUD and expose business logic to services.

### 6. Use in Routes
Import operations in your service routes.

## Secrets & Environment Variables

For sensitive values (API keys, passwords), use secrets:

```yaml
# In polytope.yml
env:
  - { name: MY_API_KEY, value: "#pt-clj (pt/secret \"my-api-key\")" }
```

Then set the secret:
```bash
pt secrets set my-api-key <value>
```

**Important**: After adding or changing environment variables, restart the sandbox:
```bash
pt run stack --mcp
```

## MCP Tools

### Viewing State
- `list-containers` - Running containers
- `list-services` - Services with ports
- `get-container-logs(container: <name>, limit: N)` - View logs

### Adding Components
- `add-and-run-service(template, name)` - Add a service
- `add-client(name, language)` - Add a client
- `add-entity(client, language, entity-singular, entity-plural)` - Add an entity
- `setup-service-for-client(service, client)` - Configure env vars

### Get Context
- `get_dev_context(scope: "models")` - Models architecture
- `get_dev_context(scope: "clients")` - Clients architecture
- `get_dev_context(scope: "api")` - API development guidelines
- `get_dev_context(scope: "frontend")` - Frontend development guidelines

## After Code Changes

**Check logs after any modification:**
```
get-container-logs(container: <service-name>, limit: 25)
```

Hot reload handles code changes automatically. **Restart only needed when changing environment variables.**

## Key Rules

1. **Services call operations** - Never call entity CRUD or clients directly
2. **Operations = business logic** - Validation, transformations, rules
3. **Entities = data + CRUD** - Extend client base classes
4. **Types = schemas** - Request/response data structures
5. **Clients = connections** - Database access, external APIs

## Language Support

- **Python**: Full support for models and clients
- **TypeScript**: Supported for models and clients
