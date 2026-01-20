# Clients

This directory contains all clients. Clients are responsible for the connection and standard SDK of networked services, such as data stores, durable execution engines, message brokers, micro services and external web services.

Clients are imported and used by models.

## Structure

For each programming language there is a sub-directory containing a library with client implementations.

## Environment Variables

Each client implementation is dependend on environment variables with configuration data needed for the connection to the services, such as URL and credentials. Clients should fail immediately when they are imported if the configuration data is missing or invalid.
