# Private Models

Internal models that should not be imported by services.

## Purpose

This directory contains helper functions, internal data transformations, and implementation details that are not part of the public API.

## When to Use

- Helper functions used by multiple operations
- Internal data transformations
- Implementation details that may change

## Example

```typescript
// models/typescript/private/validation.ts
const EMAIL_PATTERN = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

export function isValidEmail(email: string): boolean {
  return EMAIL_PATTERN.test(email);
}

export function normalizeEmail(email: string): string {
  return email.toLowerCase().trim();
}
```

Then use in public operations:

```typescript
// models/typescript/operations/users.ts
import { isValidEmail } from "../private/validation";
```

## Guidelines

1. **Not for services**: Services should never import from `private/`
2. **Internal API**: Can change without affecting services
3. **Shared helpers**: Use for code reused across operations
