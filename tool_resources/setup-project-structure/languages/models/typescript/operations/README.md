# Operations

Functions that perform business logic on entities.

## Purpose

Operations encapsulate business rules. They use clients to interact with external services and return entities. Services should call operations, not CRUD functions directly.

## Example

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

export async function getUser(userId: string): Promise<User | null> {
  const collection = getCollection("users");
  try {
    const result = await collection.get(userId);
    return result.content as User;
  } catch (error) {
    if (error.name === "DocumentNotFoundError") {
      return null;
    }
    throw error;
  }
}

export async function createUser(email: string, name: string): Promise<User> {
  // Business logic: validate email format, check uniqueness, etc.
  if (!isValidEmail(email)) {
    throw new Error("Invalid email format");
  }

  const user: User = {
    id: generateId(),
    email,
    name,
    createdAt: new Date(),
  };

  const collection = getCollection("users");
  await collection.insert(user.id, user);
  return user;
}
```

## Guidelines

1. **Document dependencies**: List client dependencies in JSDoc comments
2. **Return entities**: Operations should return entity types, not raw objects
3. **Encapsulate logic**: Validation, transformations, and rules belong here
4. **No HTTP concerns**: Operations don't know about requests/responses

## Client Dependencies

When an operation uses a client, the service importing it needs the corresponding environment variables. Document dependencies clearly:

```typescript
/**
 * Client dependencies:
 * - couchbase: COUCHBASE_CONNECTION_STRING, COUCHBASE_USERNAME, ...
 * - temporal: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, ...
 */
```

## Visibility

Operations in this directory are public. For internal helpers, use `private/`.
