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

```bash
# Add a frontend
polytope run add-and-run-service --template frontend --name my-frontend

# Add an API
polytope run add-and-run-service --template api --name my-api
```

## Running Services

Services run through Polytope:

```bash
# Run the entire stack
pt run stack --mcp

# Run a specific service
pt run my-frontend
```

## Environment Variables

Services that use models depending on clients need the appropriate environment variables. Use `setup-service-for-client` to configure them:

```bash
polytope run setup-service-for-client --service my-api --client couchbase
```

This modifies the service's `polytope.yml` to include the required environment variables.

After changing environment variables, restart the sandbox:

```bash
# Stop and restart to apply changes
pt run stack --mcp
```

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
4. **Use bin/ scripts**: Standardized scripts let any developer run the service without domain knowledge.
