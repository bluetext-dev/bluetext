# Services

This directory contains all services for the system. Services are responsible for exposing functionality through various interfaces (APIs, UIs, scheduled jobs, event handlers, etc.).

Services import and use models to implement their controller logic, keeping business logic centralized in the models layer.

## Structure

Each service has its own subdirectory with its specific implementation, configuration, and dependencies.
