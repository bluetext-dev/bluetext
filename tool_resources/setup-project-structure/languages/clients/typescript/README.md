# TypeScript Clients

TypeScript implementations of service clients.

## Usage

Import clients in your TypeScript models:

```typescript
import { getBucket, getCollection } from "@clients/typescript/couchbase";
import { getClient } from "@clients/typescript/temporal";
```

## Adding a Client

Use the `add-client` tool:

```bash
polytope run add-client --name redis --language typescript
```

## Environment Variables

Each client requires specific environment variables. The client should validate these on import and throw immediately if missing.

Example implementation pattern:

```typescript
// clients/typescript/redis/index.ts
const REDIS_URL = process.env.REDIS_URL;
if (!REDIS_URL) {
  throw new Error("REDIS_URL environment variable is required");
}

export function getClient() {
  // Return Redis client instance
}
```

## Available Clients

Clients are added as needed for your project. Common clients include:
- `couchbase` - Couchbase database
- `temporal` - Temporal workflow engine
- `postgres` - PostgreSQL database
