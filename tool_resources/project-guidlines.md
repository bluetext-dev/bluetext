# ABOUT THIS PROJECT
This project runs containerized and is orchestrated using Polytope. To interact with the running services and manage the project, specific built-in MCP tools are available. Start the MCP orchestrated Polytope Sandbox by running `pt run stack --mcp`.

*   **Execution**: Services are managed by a Polytope Sandbox.
*   **Interaction**: Your workflow consists of editing code and calling MCP tools.
*   **No Manual Execution**: **NEVER** run execution commands manually (e.g., `npm run dev`, `python main.py`).

# BEFORE MAKING CHANGES

1.  Call `get_dev_context(scope: "...")` to retrieve guidelines for specific areas (e.g., "api", "frontend", "models").
2.  Review the retrieved guidelines to ensure compliance during development.

# GENERAL DEVELOPMENT GUIDELINES

## FEATURE IMPLEMENTATION

1.  After each implementation step, use `get-container-logs` to check for any warnings or errors.
    *   Example: `get-container-logs(container: "my-api", limit: 10)`

## ENVIRONMENT VARIABLES & SECRETS

Use the provided MCP tools to manage environment variables. These tools handle necessary configuration and runtime updates.

**To add a secret or value:**
1.  Use `set-values-and-secrets` to store the value.
    *   Example: `set-values-and-secrets(...)`
2.  Use `setup-service-for-client` to inject necessary variables into a service if it relates to a client.
    *   Example: `setup-service-for-client(service: "my-api", client: "couchbase")`

**Note**: Do not edit `polytope.yml` manually for environment variables. Use the tools.

## CHECKING STATE

*   `list-containers` - View running containers.
*   `list-services` - View services and their ports.