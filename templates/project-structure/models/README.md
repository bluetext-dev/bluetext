# Models

This directory contains all models for the entire system. Models are responsible for the data structure and business logic of the system.

Models are imported and used by services, so that all of the system's data structure and business logic is centralized into one place that can be shared across services and so that services can focus on controller logic.

## Structure

For each programming language there is a sub-directory containing a library with model implementations.

## Environment Variables

Models may depend on clients that depend on certain environment variables with configuration data needed for the connection to the services, such as URL and credentials. The models should clearly specify which clients they are dependent on so that they services that import a certain model will know which environment variables are needed.
