# Test Plan: Service Naming and Dependency System (Phase 2 & 3)

## Overview

This test plan verifies the refactored `add-and-run-service` tool with the new `template-and-variables` parameter system and the `add-to-managed-services` tool.

## Key Changes to Test

1. **template-and-variables param** - Replaces old `template` param with combined template + variable overrides
2. **Renamed templates** - `postgres` → `postgres-server`, `couchbase` → `couchbase-server`
3. **New templates** - `pgweb` and `psql` as separate services with postgres connection variables
4. **Scaffold params for overrides** - Variable overrides are passed as scaffold template params, interpolated directly into the service's polytope.yml (NOT written to config/values.yml)
5. **service-config-manager** - Uses server lists (`couchbase-servers`, `postgres-servers`) that inject mounts
6. **add-to-managed-services** - Registers servers with existing config manager

---

## Test 1: Basic postgres-server

**Goal**: Verify basic service scaffolding with new param structure.

```
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "main-db", run: true)
```

**Expected**:
- Creates `services/main-db/polytope.yml`
- Creates `config/main-db/` directory
- Writes to `config/values.yml`:
  - `main-db-host: main-db`
  - `main-db-port: 5432`
  - `main-db-database: postgres`
  - `main-db-username: asdf`
- Writes to `config/secrets.yml`:
  - `main-db-password: asdfasdf`
- Runs the main-db service

---

## Test 2: Basic couchbase-server

**Goal**: Verify couchbase-server template works with new naming.

```
add-and-run-service(template-and-variables: {couchbase-server: {}}, name: "cache-db", run: true)
```

**Expected**:
- Creates `services/cache-db/polytope.yml`
- Creates `config/cache-db/` directory
- Values prefixed with `cache-db-` in config files

---

## Test 3: pgweb with default postgres connection

**Goal**: Verify pgweb template scaffolds with default postgres-server references baked in.

```
add-and-run-service(template-and-variables: {pgweb: {}}, name: "db-admin", run: false)
```

**Expected**:
- Creates `services/db-admin/polytope.yml`
- The scaffolded polytope.yml contains the default override values baked in directly:
  - `PGWEB_DATABASE_URL` contains `pt.value postgres-server-username`, `pt.secret postgres-server-password`, `pt.value postgres-server-host`, etc.
- No postgres-related entries in `config/values.yml` (pgweb has no own values)

---

## Test 4: pgweb linked to specific postgres server

**Goal**: Verify variable overrides are scaffolded directly into the service's polytope.yml.

```
# First add a postgres server
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "my-db", run: false)

# Then add pgweb linked to it
add-and-run-service(
  template-and-variables: {
    pgweb: {
      postgres-host: "pt.value my-db-host",
      postgres-port: "pt.value my-db-port",
      postgres-database: "pt.value my-db-database",
      postgres-username: "pt.value my-db-username",
      postgres-password: "pt.secret my-db-password"
    }
  },
  name: "my-pgweb",
  run: false
)
```

**Expected**:
- `services/my-pgweb/polytope.yml` contains `PGWEB_DATABASE_URL` with override values baked in:
  - `{pt.value my-db-username}`, `{pt.secret my-db-password}`, `{pt.value my-db-host}`, etc.
- No `my-pgweb-postgres-*` entries in `config/values.yml`

---

## Test 5: service-config-manager with server lists

**Goal**: Verify service-config-manager gets mounts injected for server lists.

```
# First add database servers
add-and-run-service(template-and-variables: {couchbase-server: {}}, name: "main-db", run: false)
add-and-run-service(template-and-variables: {couchbase-server: {}}, name: "cache-db", run: false)
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "auth-db", run: false)

# Add config manager with those servers
add-and-run-service(
  template-and-variables: {
    service-config-manager: {
      couchbase-servers: ["main-db", "cache-db"],
      postgres-servers: ["auth-db"]
    }
  },
  name: "config-mgr",
  run: false
)
```

**Expected**:
- Creates `services/config-mgr/polytope.yml`
- The polytope.yml mounts section should contain:
  ```yaml
  mounts:
    - path: /root/.cache/
      source: {type: volume, scope: project, id: dependency-cache}
    - path: /couchbase-servers/main-db/
      source: {type: repo, path: /config/main-db}
    - path: /couchbase-servers/cache-db/
      source: {type: repo, path: /config/cache-db}
    - path: /postgres-servers/auth-db/
      source: {type: repo, path: /config/auth-db}
  ```

---

## Test 6: add-to-managed-services

**Goal**: Verify registering a new server with an existing config manager.

```
# Setup: Add config manager first
add-and-run-service(template-and-variables: {couchbase-server: {}}, name: "main-db", run: false)
add-and-run-service(
  template-and-variables: {service-config-manager: {couchbase-servers: ["main-db"]}},
  name: "config-mgr",
  run: false
)

# Add a new server
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "new-db", run: false)

# Register it with the config manager
add-to-managed-services(service: "new-db", type: "postgres")
```

**Expected**:
- `services/config-mgr/polytope.yml` mounts section now includes:
  ```yaml
  - path: /postgres-servers/new-db/
    source: {type: repo, path: /config/new-db}
  ```
- The config manager tool is called to reapply the changes

---

## Test 7: curity with postgres variable overrides

**Goal**: Verify curity template scaffolds with postgres override values baked into the polytope.yml.

```
# Add postgres server
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "auth-db", run: false)

# Add curity linked to it
add-and-run-service(
  template-and-variables: {
    curity: {
      postgres-host: "pt.value auth-db-host",
      postgres-port: "pt.value auth-db-port",
      postgres-username: "pt.value auth-db-username",
      postgres-password: "pt.secret auth-db-password"
    }
  },
  name: "identity",
  run: false
)
```

**Expected**:
- `services/identity/polytope.yml` env section contains the overrides directly:
  - `POSTGRES_HOST` value: `pt.value auth-db-host`
  - `POSTGRES_PORT` value: `pt.value auth-db-port`
  - `POSTGRES_USERNAME` value: `pt.value auth-db-username`
  - `POSTGRES_PASSWORD` value: `pt.secret auth-db-password`
- `config/values.yml` contains curity's own values (`identity-host`, `identity-port`, etc.) but NO `identity-postgres-*` entries
- `config/secrets.yml` contains `identity-password` but NO `identity-postgres-password`

---

## Test 8: temporal with postgres variable overrides

**Goal**: Verify temporal template scaffolds with postgres override values baked into the polytope.yml.

```
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "temporal-db", run: false)

add-and-run-service(
  template-and-variables: {
    temporal: {
      postgres-host: "pt.value temporal-db-host",
      postgres-port: "pt.value temporal-db-port",
      postgres-user: "pt.value temporal-db-username",
      postgres-password: "pt.secret temporal-db-password"
    }
  },
  name: "workflow",
  run: false
)
```

**Expected**:
- `services/workflow/polytope.yml` env section contains:
  - `POSTGRES_SEEDS` value: `pt.value temporal-db-host`
  - `DB_PORT` value: `pt.value temporal-db-port`
  - `POSTGRES_USER` value: `pt.value temporal-db-username`
  - `POSTGRES_PWD` value: `pt.secret temporal-db-password`
- `config/values.yml` contains temporal's own values (`workflow-db`, `workflow-address`, etc.) but NO `workflow-postgres-*` entries

---

## Test 9: Service name validation

**Goal**: Verify that adding a service with an existing name fails.

```
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "my-db", run: false)
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "my-db", run: false)
```

**Expected**:
- Second call should fail with error: "Service 'my-db' already exists"

---

## Test 10: add-service tool (no run)

**Goal**: Verify add-service tool works with new param structure.

```
add-service(template-and-variables: {postgres-server: {}}, name: "test-db")
```

**Expected**:
- Creates service but does NOT run it
- Same scaffolding behavior as add-and-run-service with run: false

---

## Test 11: psql with env var connection

**Goal**: Verify psql uses PostgreSQL env vars (PGHOST, PGPORT, etc.) for connection.

```
add-and-run-service(template-and-variables: {postgres-server: {}}, name: "my-db", run: false)

add-and-run-service(
  template-and-variables: {
    psql: {
      postgres-host: "pt.value my-db-host",
      postgres-port: "pt.value my-db-port",
      postgres-database: "pt.value my-db-database",
      postgres-username: "pt.value my-db-username",
      postgres-password: "pt.secret my-db-password"
    }
  },
  name: "my-psql",
  run: false
)
```

**Expected**:
- `services/my-psql/polytope.yml` env section contains:
  - `PGHOST` value: `pt.value my-db-host`
  - `PGPORT` value: `pt.value my-db-port`
  - `PGUSER` value: `pt.value my-db-username`
  - `PGDATABASE` value: `pt.value my-db-database`
  - `PGPASSWORD` value: `pt.secret my-db-password`
- No Clojure connection args in the cmd block (only optional --command flag)

---

## Verification Commands

After each test, verify using MCP tools:

```
# Check service was created
describe-service(name: "<service-name>")

# List containers
list-containers()

# Check container logs
get-container-logs(container: "<service-name>")

# Read scaffolded files
Read tool: services/<name>/polytope.yml
Read tool: config/values.yml
Read tool: config/secrets.yml
```

---

## Files Modified in This Refactor

- `tool_resources/add-and-run-service/polytope.yml` - Main tool: scaffold params, removed override logic from write-service-values-to-config
- `tool_resources/add-and-run-service/postgres-server/` - Renamed from postgres
- `tool_resources/add-and-run-service/couchbase-server/` - Renamed from couchbase
- `tool_resources/add-and-run-service/pgweb/` - New template, uses `{ {{ var }} }` for embedded URL context
- `tool_resources/add-and-run-service/psql/` - New template, refactored to use PGHOST/PGPORT/etc env vars
- `tool_resources/add-and-run-service/service-config-manager/template/polytope.yml` - Simplified
- `tool_resources/add-and-run-service/curity/template/polytope.yml` - Uses `{{ postgres-host }}` scaffold params
- `tool_resources/add-and-run-service/temporal/template/polytope.yml` - Uses `{{ postgres-host }}` scaffold params
- `tool_resources/set-values-and-secrets/add-and-run-service/curity/` - Removed postgres entries from values/secrets
- `tool_resources/set-values-and-secrets/add-and-run-service/temporal/` - Removed postgres entries from values/secrets
- `tool_resources/add-to-managed-services/polytope.yml` - New tool
- `tool_resources/polytope.yml` - Added register tool to includes
