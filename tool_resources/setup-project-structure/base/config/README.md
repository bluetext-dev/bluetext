# Config

This directory contains configuration files for the project, such as environment variable values and secrets.

## Values and Secrets

Configuration is managed through **Values** and **Secrets**:

*   **Values**: Non-sensitive configuration (e.g., `USE_AUTH`, `API_URL`).
*   **Secrets**: Sensitive data (e.g., `API_KEY`, `DB_PASSWORD`).

## Management

Use MCP tools to manage configuration:

1.  **Set values/secrets**:
    `set-values-and-secrets(...)`

2.  **Inject into services**:
    `setup-service-for-client(...)`

These tools modify the configuration files in this directory and update running services automatically.