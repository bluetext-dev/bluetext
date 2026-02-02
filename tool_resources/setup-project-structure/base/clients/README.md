# Clients

Clients handle connections to external services: databases, message brokers, APIs, and other networked resources.

## Purpose

Clients provide a standardized SDK for interacting with external services. They abstract connection logic, authentication, and basic operations so that models can focus on business logic.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Services   │ ──▶ │    Models    │ ──▶ │   Clients    │ ──▶ External Services
└──────────────┘     └──────────────┘     └──────────────┘
```

**Clients are imported by models, not services directly.**

## Structure

```
clients/
├── python/
│   ├── pyproject.toml
│   └── clients/          # The importable package
│       ├── couchbase/    # Couchbase client
│       ├── temporal/     # Temporal client
│       └── ...
└── README.md
```

## Usage

Import clients in your models:

```python
from clients.couchbase import get_bucket, get_collection
from clients.temporal import get_client
```

The nested `clients/python/clients/` structure allows the package at `clients/python` to expose `clients` as the importable package name.

## Environment Variables

Each client depends on environment variables for configuration (URLs, credentials, etc.). Clients should **fail immediately on import** if required configuration is missing.

Example client environment variables:
```
COUCHBASE_CONNECTION_STRING=couchbase://localhost
COUCHBASE_USERNAME=admin
COUCHBASE_PASSWORD=password
COUCHBASE_BUCKET=default
```

## Adding Clients to Services

To use a client in a service, the service must have the required environment variables configured. Use the `setup-service-for-client` tool to add them:

```
setup-service-for-client(service: "my-api", client: "couchbase-client")
```

This adds the necessary environment variable definitions to the service's `polytope.yml`.

## Adding a New Client

Use the `add-client` tool to scaffold a new client:

```
add-client(name: "couchbase", language: "python")
```

See the language-specific README in `clients/<language>/` for implementation details.