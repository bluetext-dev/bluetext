export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public details: string,
    public body?: unknown,
  ) {
    super(`${code}: ${details}`);
    this.name = "ApiError";
  }
}

const CLIENT_ID = "{{ project-name }}";
const ENV_KEY = `VITE_${CLIENT_ID.replace(/-/g, "_").toUpperCase()}_URL`;
const env = import.meta.env as Record<string, string | undefined>;
const BASE_URL = env[ENV_KEY];

if (!BASE_URL) {
  throw new Error(
    `Missing environment variable: ${ENV_KEY}\n` +
    `Add to your .env file: ${ENV_KEY}=<url>`,
  );
}

async function request<T>(
  method: string,
  path: string,
  data?: unknown,
): Promise<T> {
  const headers: Record<string, string> = {
    accept: "application/json",
  };

  if (data !== undefined) {
    headers["content-type"] = "application/json";
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    credentials: "include",
    body: data !== undefined ? JSON.stringify(data) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  if (response.ok) {
    return (await response.json()) as T;
  }

  let code = "server_error";
  let details = response.statusText;
  let body: unknown;

  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    body = await response.json();
    const b = body as Record<string, string>;
    code = b.code ?? b.error_code ?? code;
    details = b.message ?? b.detail ?? b.detailed_error ?? details;
  }

  throw new ApiError(response.status, code, details, body);
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, data?: unknown) => request<T>("POST", path, data),
  put: <T>(path: string, data?: unknown) => request<T>("PUT", path, data),
  patch: <T>(path: string, data?: unknown) => request<T>("PATCH", path, data),
  del: <T>(path: string) => request<T>("DELETE", path),
};
