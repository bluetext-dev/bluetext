# TypeScript Clients

TypeScript client libraries for connecting to services.

## API Client Walkthrough

To connect a frontend service (e.g., `my-web`) to a backend API (e.g., `my-api`):

### 1. Add the client

```
add-client(template: "api", language: "typescript", target: "my-api")
```

This scaffolds a typed API client at `clients/typescript/my-api-client/` with:
- `client.ts` — base HTTP client with error handling
- `endpoints.ts` — typed endpoint functions (auto-generated)

### 2. Configure the consumer service

```
setup-service-for-client(client-type: "python-fast-api", consumer: "my-web", upstream: "my-api")
```

This injects the required environment variable (e.g., `VITE_MY_API_CLIENT_URL`) into the consumer service's `polytope.yml` and reapplies the stack so the container picks it up.

### 3. Sync the API client

```
sync-api-client(target: "my-api")
```

This reads the OpenAPI spec from the running API service and generates typed endpoint functions in `endpoints.ts`. Re-run this whenever the API changes.

### 4. Import and use

```typescript
import { health } from "@clients/my-api-client/endpoints";

const result = await health.list();
```

The `@clients` path alias is configured in the service's `tsconfig.json` and maps to the mounted `clients/typescript/` directory.

## Adding Other Clients

Use the `add-client` tool with the appropriate template:

```
add-client(template: "couchbase", language: "typescript")
add-client(template: "temporal", language: "typescript")
```

## Environment Variables

Each client reads its configuration from environment variables. The API client uses `VITE_<CLIENT_ID>_URL` where `CLIENT_ID` is derived from the client directory name (e.g., `VITE_MY_API_CLIENT_URL` for `my-api-client`).

Use `setup-service-for-client` to inject these variables automatically.
