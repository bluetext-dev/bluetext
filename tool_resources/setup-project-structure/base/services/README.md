# Services

Services expose functionality through interfaces: APIs, frontends, scheduled jobs, event handlers, and more.

## Purpose

Services handle controller logic: routing, authentication, request/response handling, and orchestration. Business logic belongs in models, not services.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Services   │ ──▶ │    Models    │ ──▶ │   Clients    │
│  - APIs      │     │  (business   │     │  (external   │
│  - Frontends │     │    logic)    │     │   services)  │
│  - Workers   │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Structure

```
services/
├── my-api/           # API service
│   ├── polytope.yml  # Container configuration
│   ├── bin/          # Run scripts
│   └── ...
├── my-frontend/      # Frontend service
│   ├── polytope.yml
│   ├── app/          # React application
│   └── ...
└── README.md
```

Each service has its own directory with a `polytope.yml` that defines how it runs.

## Adding a Service

Use `add-and-run-service` to scaffold and start a new service:

```
# Add a frontend
add-and-run-service(template: "frontend_typescript_react-router-v7", name: "my-frontend")

# Add an API
add-and-run-service(template: "api_python_fastapi", name: "my-api")
```

## Running Services

Services run through Polytope automatically in the sandbox. Use MCP tools to interact with them.

```
# View logs
get-container-logs(container: "my-frontend", limit: 50)
```

## Environment Variables

Services that use models depending on clients need the appropriate environment variables. Use `setup-service-for-client` to configure them:

```
setup-service-for-client(service: "my-api", client: "couchbase")
```

This modifies the service's `polytope.yml` to include the required environment variables.

## Service Types

### Frontend
React-based web applications. See the frontend template README for styling, routing, and component guidelines.

### API
Backend services that expose HTTP endpoints. Import models to handle business logic.

### Workers
Background processors, scheduled jobs, or event handlers.

## Best Practices

1. **Keep services thin**: Controller logic only. Business logic goes in models.
2. **Use models for data access**: Don't import clients directly in services.
3. **Document dependencies**: Note which models (and therefore clients) the service uses.