# TypeScript Models

TypeScript implementations of entities and operations.

## Structure

```
models/typescript/
├── entities/       # Data structures (public)
├── operations/     # Business logic functions (public)
├── private/        # Internal models, not exported
└── README.md
```

## Usage

Import models in your TypeScript services:

```typescript
import { User } from "@models/typescript/entities/user";
import { getUser, createUser } from "@models/typescript/operations/users";
```

## Adding Models

### Entities

Create entity files in `entities/`:

```typescript
// models/typescript/entities/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
}
```

### Operations

Create operations in `operations/`:

```typescript
// models/typescript/operations/users.ts
/**
 * User operations.
 *
 * Client dependencies:
 * - couchbase
 */
import { getCollection } from "@clients/typescript/couchbase";
import type { User } from "../entities/user";

export async function getUser(userId: string): Promise<User> {
  const collection = getCollection("users");
  const result = await collection.get(userId);
  return result.content as User;
}

export async function createUser(email: string, name: string): Promise<User> {
  // Business logic here
}
```

## Client Dependencies

Document which clients your operations depend on. Services importing these operations need the corresponding environment variables configured.

See `operations/README.md` and `entities/README.md` for more details.
