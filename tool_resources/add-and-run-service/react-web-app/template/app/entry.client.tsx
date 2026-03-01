import { startTransition } from "react";
import { hydrateRoot } from "react-dom/client";
import { HydratedRouter } from "react-router/dom";

// Note: StrictMode is intentionally omitted here.
// React Router v7's default entry.client.tsx wraps in <StrictMode>, which
// double-fires useEffect in dev mode. This breaks OAuth flows because auth
// codes are single-use — the second call fails with 401.
startTransition(() => {
  hydrateRoot(document, <HydratedRouter />);
});
