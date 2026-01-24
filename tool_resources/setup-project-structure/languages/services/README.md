# Services

This directory contains all services for the system.

See `services/README.md` in your project root for an overview of the services architecture.

## Adding Services

Use `add-and-run-service` to scaffold a new service:

```bash
polytope run add-and-run-service --template frontend --name my-frontend
polytope run add-and-run-service --template api --name my-api
```

## Structure

Each service has its own subdirectory:

```
services/
├── my-api/
│   ├── polytope.yml    # Container configuration
│   ├── bin/            # Run scripts
│   └── ...
├── my-frontend/
│   ├── polytope.yml
│   ├── app/            # React application
│   └── ...
└── README.md
```
