# Bluetext Development Framework

## Environment

This project is built with the **Bluetext framework**, which runs a **containerized environment orchestrated by Polytope**.

*   **`initialize-session`**: By calling this tool it is ensured the project stack is running. These are development instructions for the project.
*   **Execution**: Services of this project are already running containerized and are managed by a Polytope Sandbox.
*   **Interaction**: Your workflow consists of editing code and calling MCP tools.

## Rules

1.  **No Manual Execution**: Execution is handled through Polytope. The containerized environment can be interacted with through MCP tool calls. **NEVER** run execution commands manually (e.g., `npm run dev`, `python main.py`). Seeing this message means stack is already running. 
2.  **Check Logs**: Always check logs after making modifications to verify success: `get-container-logs(container: <service-name>, limit: 10)`.
3.  **Environment Variables**: Use provided tools (like `setup-service-for-client` or `set-values-and-secrets`) to manage environment variables. These tools handle necessary runtime updates.

## Project Structure

```
project/
├── services/
│   ├── my-frontend/
│   ├── my-api/
│   ├── couchbase/    # Datastore service
│   └── temporal/     # Workflow service
├── models/
│   └── python/
│       └── models/
│           ├── entities/
│           ├── operations/
│           └── types/
├── clients/
│   └── python/
│       └── clients/
│           └── couchbase/
└── config/           # Values and secrets
```

## Architecture

```
Services → Operations → Entities → Clients → Datastore
               ↑
             Types
```

*   **Services**: Any running component (Frontends, APIs, Datastores, Workflow Engines).
*   **Operations**: Public business logic that services call.
*   **Entities**: Data structures with CRUD, extending client base classes.
*   **Types**: Ephemeral data structures (requests, responses, etc.).
*   **Resources**: The combination of an Entity + its Types + Operations. A resource is a complete data-backed concept with full CRUD business logic.
*   **Endpoints**: A Resource + API routes registered in a service. A full vertical slice from data model to HTTP API.
*   **Clients**: Connections to external services, like datastore servers.
*   **Config**: Holds all data required for configurations. E.g. values and secrets for environment variables.

## Guidelines

1.  **Services call operations**: Never call entity CRUD or clients directly.
2.  **Operations = business logic**: Validation, transformations, rules.
3.  **Entities = data + CRUD**: Extend client base classes.
4.  **Types = schemas**: Request/response data structures.
5.  **Clients = connections**: Database access, external APIs.
6.  **Controllers utilize Operations**: Services act as controllers. A controller has a n:1 relationship to an operation (e.g., an API endpoint should call no more than one operation).

## Available Templates

### Services
*   `api_python_fastapi` - Python FastAPI backend
*   `frontend_typescript_react-router-v7` - React TypeScript frontend
*   `couchbase-server_enterprise-v7` - Couchbase database
*   `postgres` - PostgreSQL database
*   `temporal` - Temporal workflow engine
*   `temporal-ui` - Temporal web UI

### Clients
*   `couchbase` - Couchbase database client
*   `temporal` - Temporal workflow client

## Typical Workflow

### 1. Add Services
```
add-and-run-service(template: "api_python_fastapi", name: "api")
add-and-run-service(template: "couchbase-server_enterprise-v7", name: "frontend")
```

### 2. Add Client
Connect services to a datastore. This scaffolds client code and sets values/secrets for other services (like the API) to use.
```
add-client(name: "couchbase", language: "python")
```

### 3. Configure Service for Client
Sets environment variables for a service to use a client. No restart is required.
```
setup-service-for-client(service: "api", client: "couchbase-client")
```

### 4. Add Endpoint (Recommended)
Scaffold a full vertical slice: entity + types + operations + API routes.
```
add-endpoint(client: "couchbase", language: "python", entity-singular: "task", entity-plural: "tasks", fields: [{name: "title", type: "str"}, {name: "done", type: "bool"}], service: "python-fast-api")
```

Or scaffold only specific layers:
```
add-endpoint(layers: ["entity", "resource"], ...)  # Entity + types + operations, no routes
add-entity(...)                                      # Entity only (no types/operations/routes)
```

### 5. Customize
Customize the generated operations, types, or routes as needed for your business logic.

## Secrets & Environment Variables

Tools scaffolding logic using values/secrets also scaffold those values/secrets with defaults.

**Usage:**

```yaml
# In polytope.yml
env:
  - { name: MY_API_KEY, value: pt.secret my-api-key }
```

## MCP Tools

### Viewing State (Built-in Polytope Tools)
*   `list-containers` - Running containers
*   `list-services` - Services with ports
*   `get-container-logs(container: <name>, limit: N)` - View logs

### Adding Components
*   `add-and-run-service(template, name)` - Add a service
*   `add-client(name, language)` - Add a client
*   `add-endpoint(client, language, entity-singular, entity-plural, fields, service)` - Add a full endpoint (entity + types + operations + routes)
*   `add-entity(client, language, entity-singular, entity-plural, fields)` - Add an entity only
*   `setup-service-for-client(service, client)` - Configure env vars

### Get Context
*   `get-dev-context(scope: "models")` - Models architecture
*   `get-dev-context(scope: "clients")` - Clients architecture
*   `get-dev-context(scope: "python-fast-api")` - API development guidelines
*   `get-dev-context(scope: "react-web-app")` - Frontend development guidelines