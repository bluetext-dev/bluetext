# General Development Guidelines

This project uses Bluetext architecture: services, models, and clients organized for enterprise-grade development.

## Architecture Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Services   │ ──▶ │    Models    │ ──▶ │   Clients    │ ──▶ External Services
│  (controller │     │  (business   │     │  (connections │
│    logic)    │     │    logic)    │     │   to DBs,    │
│              │     │              │     │   APIs, etc) │
└──────────────┘     └──────────────┘     └──────────────┘
```

- **Services**: Frontends, APIs, workers. Handle routing, auth, request/response. Import models.
- **Models**: Business logic. Entities (data structures) and Operations (functions). Import clients.
- **Clients**: Connections to external services (Couchbase, Temporal, etc.). Require environment variables.

## Project Structure

```
project/
├── services/           # Frontends, APIs, workers
│   ├── my-frontend/
│   └── my-api/
├── models/             # Business logic (shared across services)
│   └── python/
│       ├── entities/   # Data structures
│       └── operations/ # Business functions
├── clients/            # Service connections
│   └── python/
│       └── couchbase/
└── config/             # Values and secrets
```

## Key Principles

1. **Services are thin**: Controller logic only. Business logic goes in models.
2. **Models use clients**: Don't import clients directly in services.
3. **Operations over CRUD**: Services call operations, not raw database calls.
4. **Environment variables**: Clients require env vars. Use `setup-service-for-client` to configure.

## MCP Tools

### Viewing State
- `list-containers` - Running containers
- `list-services` - Services with ports
- `get-container-logs(container: <name>, limit: N)` - View logs

### Adding Components
- `add-and-run-service(template: "frontend", name: "my-frontend")` - Add a service
- `setup-project-structure(language: "python")` - Initialize models/clients structure
- `add-client(name: "couchbase", language: "python")` - Add a client
- `setup-service-for-client(service: "my-api", client: "couchbase-client")` - Configure env vars

### After Code Changes

**MANDATORY**: Check logs after any modification:
```
get-container-logs(container: <service-name>, limit: 25)
```

Hot reload is enabled. No manual restarts needed unless adding environment variables.

## Environment Variables

When a service uses models that depend on clients, configure the env vars:

```bash
# 1. Set values and secrets
polytope run set-values-and-secrets --source couchbase-client

# 2. Add env vars to service
polytope run setup-service-for-client --service my-api --client couchbase-client

# 3. Restart sandbox to apply
pt run stack --mcp
```

## Documentation

Each directory has a README.md explaining its purpose:
- `clients/README.md` - Client architecture and env vars
- `models/README.md` - Entities vs Operations
- `services/README.md` - Service types and best practices
