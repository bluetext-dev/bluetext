# Frontend Development Guidelines

React Router v7 with Bun, TypeScript, Tailwind CSS, and shadcn/ui components.

## Project Structure

```
app/
├── components/ui/    # 45+ shadcn/ui components
├── hooks/            # Custom React hooks
├── lib/              # Utilities
├── routes/           # Route components
├── root.tsx          # Root layout, theme detection
├── routes.ts         # Route configuration
└── app.css           # Global styles
```

## Import Paths (CRITICAL)

**Use `~` for `app/` directory:**
```tsx
import { Button } from "~/components/ui/button";
import { HomePage } from "~/routes/home";
```

**Use `@` for project root:**
```tsx
import type { User } from "@/models/typescript/models/entities/user";
```

**Rule**: `app/` = `~`, project root = `@`

## Adding Routes

Routes are defined in `app/routes.ts`:

```ts
import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("users/:id", "routes/user-detail.tsx"),
] satisfies RouteConfig;
```

Each route exports: `meta`, `default`, `loader` (optional), `action` (optional).

## Styling

### Theme-Aware Classes (REQUIRED)
```tsx
// CORRECT
<div className="bg-background text-foreground">
<div className="bg-card text-card-foreground">

// WRONG - breaks dark mode
<div className="bg-white text-black">
```

**Available**: `background`, `foreground`, `card`, `primary`, `secondary`, `accent`, `destructive`, `muted`, `border`, `input`, `ring` (all with `-foreground` variants)

### Opacity Modifiers
```tsx
<div className="bg-primary/10">            // 10% opacity
<div className="text-muted-foreground/50"> // 50% opacity
```

## Components

**Always use shadcn/ui components:**
```tsx
// CORRECT
import { Button } from "~/components/ui/button";
<Button variant="destructive">Delete</Button>

// WRONG
<button className="px-4 py-2 bg-primary...">Delete</button>
```

Available: Accordion, AlertDialog, Alert, AspectRatio, Avatar, Badge, Breadcrumb, Button, Calendar, Card, Carousel, Chart, Checkbox, Collapsible, Command, ContextMenu, Dialog, Drawer, DropdownMenu, Form, HoverCard, InputOTP, Input, Label, Menubar, NavigationMenu, Pagination, Popover, Progress, RadioGroup, Resizable, ScrollArea, Select, Separator, Sheet, Sidebar, Skeleton, Slider, Sonner, Switch, Table, Tabs, Textarea, ToggleGroup, Toggle, Tooltip.

## API Integration

Import types from the models library:

```tsx
import type { User } from "@/models/typescript/models/entities/user";
import type { LoginRequest } from "@/models/typescript/models/types/auth";

export async function loader({ params }: Route.LoaderArgs) {
  const response = await fetch(`/api/users/${params.id}`);
  return { user: await response.json() as User };
}
```

If using models that depend on clients, configure env vars:
```
setup-service-for-client(service: "<frontend>", client: "couchbase-client")
```

## Adding Dependencies

Call the service-specific tool:
```
<service-name>-add-dependencies(packages: "axios react-query")
```

## After Code Changes

Hot reload is enabled. Check logs if something breaks:
```
get-container-logs(container: "<frontend-name>", limit: 25)
```

## Key Rules

1. **Use `~` for app/, `@` for root** - Import paths matter
2. **Theme classes only** - Never use fixed colors like `bg-white`
3. **shadcn components first** - Don't reinvent UI elements
4. **Types from models** - Import entities and types from models library