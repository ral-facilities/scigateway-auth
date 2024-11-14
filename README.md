[![Build Status](https://github.com/ral-facilities/scigateway-auth/workflows/CI/badge.svg?branch=main)](https://github.com/ral-facilities/scigateway-auth/actions?query=workflow%3A%22CI%22)
[![Codecov](https://codecov.io/gh/ral-facilities/scigateway-auth/branch/main/graph/badge.svg)](https://codecov.io/gh/ral-facilities/scigateway-auth)

# SciGateway Auth

This is a Python microservice created using FastAPI that provides an Authentication REST API for the SciGateway web
application.

## How to Run

This microservice requires an ICAT server to run against.

### Prerequisites

- Docker and Docker Compose installed (if you want to run the microservice inside Docker)
- Python 3.11 installed on your machine (if you are not using Docker)
- ICAT server to connect to
- Private and public key pair (must be OpenSSH encoded) for encrypting and decrypting the JWTs
- This repository cloned

### Docker Setup

Ensure that Docker is installed and running on your machine before proceeding.

#### Prerequisite Steps

1. Create a `.env` file alongside the `.env.example` file. Use the example file as a reference and modify the values
   accordingly.

   ```bash
   cp scigateway_auth/.env.example scigateway_auth/.env
   ```

2. Create a `logging.ini` file alongside the `logging.example.ini` file. Use the example file as a reference and modify
   it accordingly:

   ```bash
   cp scigateway_auth/logging.example.ini scigateway_auth/logging.ini
   ```

3. Generate OpenSSH encoded private and public key pair in the `keys` directory:

   ```bash
   ssh-keygen -b 2048 -t rsa -f keys/jwt-key -q -N "" -C ""
   ```

#### Using `docker-compose.yml` for local development

The easiest way to run the application with Docker for local development is using the `docker-compose.yml` file. It is
configured to mount the `scigateway_auth` directory to the container via a volume which means that FastAPI will watch
for changes made to the code and automatically reload the application on the fly. This is useful as you do not have to
rebuild the image and start the container again each time you make a change.

1. Build and start the Docker container:
   ```bash
   docker-compose up
   ```
   The microservice should now be running inside Docker at http://localhost:8000 and its Swagger UI could be accessed
   at http://localhost:8000/docs.

#### Using `Dockerfile` for local development

Use the `Dockerfile`'s `dev` stage to run just the application itself in a container. Use this only for local
development (not production)! Mounting the `scigateway_auth` directory to the container via a volume means that FastAPI
will watch for changes made to the code and automatically reload the application on the fly. This is useful as you do
not have to rebuild the image and start the container again each time you make a change.

1. Build an image using the `Dockerfile`'s `dev` stage from the root of the project directory:

   ```bash
   docker build --file Dockerfile --target dev --tag scigateway-auth:dev .
   ```

2. Start the container using the image built and map it to port `8000` locally (please note that the public key volume
   is only needed if JWT Auth is enabled):

   ```bash
   docker run --publish 8000:8000 --name scigateway-auth --volume ./scigateway_auth:/app/scigateway_auth --volume ./keys/jwt-key:/app/keys/jwt-key --volume ./keys/jwt-key.pub:/app/keys/jwt-key.pub --volume ./maintenance/maintenance.json:/app/maintenance/maintenance.json --volume ./maintenance/scheduled_maintenance.json:/app/maintenance/scheduled_maintenance.json scigateway-auth:dev
   ```

   or with values for the environment variables:

   ```bash
   docker run --publish 8000:8000 --name scigateway-auth --env AUTHENTICATION__REFRESH_TOKEN_VALIDITY_DAYS=14 --volume ./scigateway_auth:/app/scigateway_auth --volume ./keys/jwt-key:/app/keys/jwt-key --volume ./keys/jwt-key.pub:/app/keys/jwt-key.pub --volume ./maintenance/maintenance.json:/app/maintenance/maintenance.json --volume ./maintenance/scheduled_maintenance.json:/app/maintenance/scheduled_maintenance.json scigateway-auth:dev
   ```

   The microservice should now be running inside Docker at http://localhost:8000 and its Swagger UI could be accessed
   at http://localhost:8000/docs.

#### Using `Dockerfile` for running the tests

Use the `Dockerfile`'s `test` stage to run the tests in a container. Mounting the `scigateway_auth` and `test`
directories to the container via volumes means that any changes made to the application or test code will automatically
be synced to the container next time you run the tests. This is useful as you do not have to rebuild the image each
time you make a change.

1. Build an image using the `Dockerfile`'s `test` stage from the root of the project directory:

   ```bash
   docker build --file Dockerfile --target test --tag scigateway-auth:test .
   ```

2. Run the tests using:

   ```bash
   docker run --rm --name scigateway-auth --volume ./scigateway_auth:/app/scigateway_auth --volume ./test:/app/test scigateway-auth:test
   ```
