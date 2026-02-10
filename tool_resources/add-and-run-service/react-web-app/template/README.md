# Frontend Service

React Router v7 application with Bun, TypeScript, Tailwind CSS, and shadcn/ui components.

## Development

### Running the Service

The frontend runs through Polytope. From your project root:

```bash
# Start the stack (includes frontend)
pt run stack --mcp

# Or run just this service
pt run <service-name>
```

Hot reloading is enabled by default. Changes to files in `app/` will automatically reflect in the browser without restarting the container.

### Adding Dependencies

Use the Polytope module to add packages:

```bash
polytope run <service-name>-add --packages "axios react-query"
```

### Adding Routes

Routes are defined in `app/routes.ts` using React Router 7's configuration API:

```ts
import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("about", "routes/about.tsx"),
  route("users/:id", "routes/user-detail.tsx"),
] satisfies RouteConfig;
```

Each route file exports:
- `meta` - Page title and meta tags
- `default` - The page component
- `loader` (optional) - Server-side data fetching
- `action` (optional) - Form submissions

Example route file:

```tsx
import type { Route } from "./+types/about";

export function meta({}: Route.MetaArgs) {
  return [{ title: "About" }];
}

export default function About() {
  return <div>About page</div>;
}
```

## Project Structure

```
app/
├── components/
│   └── ui/              # shadcn/ui components (45+)
├── hooks/               # Custom React hooks
├── lib/                 # Utilities (cn, etc.)
├── routes/              # Route components
├── root.tsx             # Root layout, theme detection
├── routes.ts            # Route configuration
└── app.css              # Global styles, CSS variables

bin/
├── init                 # Runs bun install
└── run                  # Starts dev server

polytope.yml             # Container and service config
vite.config.ts           # Build configuration
```

## Styling & Components

### Import Paths

**Use `~` for imports from `app/` directory:**

```tsx
import { Button } from "~/components/ui/button";
import { HomePage } from "~/routes/home";
```

**Use `@` for imports from project root:**

```tsx
import { apiClient } from "@/lib/apiClient";
```

### Theme System

Use semantic color classes that adapt to light/dark mode automatically:

```tsx
// Correct - theme-aware
<div className="bg-background text-foreground">
<div className="bg-card text-card-foreground">
<Button className="bg-primary text-primary-foreground">

// Wrong - breaks in dark mode
<div className="bg-white text-black">
<div className="bg-gray-50 text-gray-900">
```

**Available semantic classes:**
- **Layout**: `background`, `foreground`
- **Components**: `card`, `popover`, `muted` (with `-foreground` variants)
- **Interactive**: `primary`, `secondary`, `accent`, `destructive` (with `-foreground`)
- **Form/UI**: `border`, `input`, `ring`

For color variations, use opacity modifiers:

```tsx
<div className="bg-primary/10">            // 10% opacity
<div className="text-muted-foreground/50"> // 50% opacity
```

### Available Components

The template includes 45+ shadcn/ui components:

**Forms**: Button, Input, Textarea, Checkbox, Radio Group, Select, Switch, Toggle, Slider

**Layout**: Card, Dialog, Drawer, Sheet, Accordion, Collapsible, Separator, Tabs

**Display**: Badge, Avatar, Skeleton, Progress, Alert, Table

**Navigation**: Breadcrumb, Pagination, Navigation Menu, Dropdown Menu

**Interactive**: Command, Calendar, Hover Card, Popover, Tooltip

**Feedback**: Toast (Sonner)

Always use shadcn components instead of custom HTML:

```tsx
// Correct
import { Button } from "~/components/ui/button";
<Button variant="destructive">Delete</Button>

// Wrong
<button className="px-4 py-2 bg-primary...">Delete</button>
```

## API Integration

The frontend connects to backend services through the models library. Import operations that encapsulate business logic:

```tsx
import { getUser, createUser } from "@models/typescript/operations/users";
import type { User } from "@models/typescript/entities/user";

// In a React Router loader
export async function loader({ params }: Route.LoaderArgs) {
  const user = await getUser(params.id);
  return { user };
}

// In a component
export default function UserProfile({ loaderData }: Route.ComponentProps) {
  const { user } = loaderData;
  return <div>{user.name}</div>;
}
```

### Architecture Overview

```
Frontend (this service)
    │
    ▼
Models (business logic)      ──▶  models/README.md
    │
    ▼
Clients (service connections) ──▶  clients/README.md
    │
    ▼
External Services (databases, APIs, etc.)
```

### Setting Up Service Connections

If your frontend needs to use models that depend on clients (e.g., fetching data from Couchbase), configure the environment variables:

```bash
polytope run setup-service-for-client --service <this-service> --client couchbase
```

Then restart the sandbox to apply changes.

### Related Documentation

- `../../models/README.md` - Models architecture and operations/entities
- `../../clients/README.md` - Client setup and environment variables
- `../../models/typescript/operations/README.md` - Writing TypeScript operations

## Why This Stack

This template is optimized for building enterprise-grade systems efficiently.

### Developer Experience
- **Fast startup**: Bun runtime enables quick spin up/down of the development environment
- **Hot reloading**: All file changes reflect immediately without container restarts
- **Unified logs**: Easy overview of all logs across container restarts
- **Cross-domain friendly**: Developers from different domains can run the stack without memorizing commands outside their expertise

### AI-Assisted Development
- **React**: Extensive training data and resources available
- **React Router 7**: Routing configuration is understandable at a glance
- **shadcn/ui**: Reduces token usage while staying customizable, no special patterns to learn
- **Tailwind CSS**: Generates well with AI assistance

### Portability & Collaboration
- **Polytope**: Single config file defines everything needed to run
- **One command**: `pt run stack --mcp` starts the entire environment
- **Reproducible**: Consistent behavior across operating systems and development environments
- **Containerized**: Alpine Linux with optimized caching for fast rebuilds

## Configuration Files

| File | Purpose |
|------|---------|
| `polytope.yml` | Container config, environment variables, ports, health checks |
| `vite.config.ts` | Build tool config, path aliases, plugins |
| `tsconfig.json` | TypeScript compiler options, path mappings |
| `react-router.config.ts` | SSR settings (enabled by default) |
| `components.json` | shadcn/ui configuration (style, aliases) |
| `tailwind.config.ts` | Tailwind CSS customization |
