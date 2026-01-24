# Entities

Data structures that define the shape of your data.

## Purpose

Entities are pure type definitions. They should not contain business logic or side effects.

## Example

```typescript
// models/typescript/entities/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
  updatedAt?: Date;
}
```

## Guidelines

1. **Use interfaces or types**: Prefer `interface` for objects, `type` for unions
2. **No side effects**: Entities should not import clients or perform I/O
3. **Type everything**: Avoid `any`, use proper types
4. **Keep it simple**: Entities are data, not behavior

## Visibility

Entities in this directory are public and can be imported by services. For internal-only entities, use `private/`.
