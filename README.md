[![Build Status](https://github.com/ral-facilities/scigateway-auth/workflows/CI/badge.svg?branch=main)](https://github.com/ral-facilities/scigateway-auth/actions?query=workflow%3A%22CI%22)
[![Codecov](https://codecov.io/gh/ral-facilities/scigateway-auth/branch/main/graph/badge.svg)](https://codecov.io/gh/ral-facilities/scigateway-auth)

# SciGateway Auth

This is a Python microservice created using FastAPI that provides an Authentication REST API for the SciGateway web
application.

## How to Run Locally

This microservice requires an ICAT server to run against.

### Prerequisites

- Docker and Docker Compose installed (if you want to run the microservice inside Docker)
- Python 3.11 and Poetry installed on your machine (if you are not using Docker)
- ICAT server to connect to
- Private and public key pair (must be OpenSSH encoded) for encrypting and decrypting the JWTs
- This repository cloned

### Prerequisite Steps

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

### Inside of Docker

Ensure that Docker is installed and running on your machine before proceeding.

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

2. Start the container using the image built and map it to port `8000` locally:

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

### Outside of Docker

Ensure that Python and Poetry are installed on your machine before proceeding. To install Poetry,
follow [the instructions](https://python-poetry.org/docs/#installing-with-the-official-installer) from their
documentation.

1. Install the project's dependencies:

   ```bash
   poetry install
   ```
   
2. Start the application:

   ```bash
   fastapi dev scigateway_auth/main.py --host 0.0.0.0 --port 8000
   ```

   The microservice should now be running in development mode at http://localhost:8000 and its Swagger UI could be
   accessed at http://localhost:8000/docs. FastAPI will watch for changes made to the code and automatically reload the
   application on the fly.

## Notes

### Application Configuration

The configuration for the application is handled
using [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). It allows for loading config
values from environment variables or the `.env` file. Please note that even when using the `.env` file, Pydantic will
still read environment variables as well as the `.env` file, environment variables will always take priority over values
loaded from the `.env` file.

Listed below are the environment variables supported by the application.

| Environment Variable                            | Description                                                                                                               | Mandatory | Default Value |
|-------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|-----------|---------------|
| `API__ROOT_PATH`                                | (If using a proxy) The path prefix handled by a proxy that is not seen by the app.                                        | No        | ` `           |
| `API__ALLOWED_CORS_HEADERS`                     | The list of headers that are allowed to be included in cross-origin requests.                                             | Yes       |               |
| `API__ALLOWED_CORS_ORIGINS`                     | The list of origins (domains) that are allowed to make cross-origin requests.                                             | Yes       |               |
| `API__ALLOWED_CORS_METHODS`                     | The list of methods that are allowed to be used to make cross-origin requests.                                            | Yes       |               |
| `AUTHENTICATION__PRIVATE_KEY_PATH`              | The path to the private key to be used for encoding JWT access and refresh tokens.                                        | Yes       |               |
| `AUTHENTICATION__PUBLIC_KEY_PATH`               | The path to the public key to be used for decoding JWT access and refresh tokens signed by the corresponding private key. | Yes       |               |
| `AUTHENTICATION__JWT_ALGORITHM`                 | The algorithm to use to decode and encode the JWT access and refresh tokens.                                              | Yes       |               |
| `AUTHENTICATION__ACCESS_TOKEN_VALIDITY_MINUTES` | Minutes after which the JWT access token expires.                                                                         | Yes       |               |
| `AUTHENTICATION__REFRESH_TOKEN_VALIDITY_DAYS`   | Days after which the JWT refresh token expires.                                                                           | Yes       |               |
| `AUTHENTICATION__JWT_REFRESH_TOKEN_BLACKLIST`   | The list of blacklisted JWT refresh tokens which when received will reject to refresh the provided access token.          | Yes       |               |
| `AUTHENTICATION__ADMIN_USERS`                   | The list of admin users. These are the ICAT usernames of the users normally in the `<icat-mnemonic>/<username>` form.     | Yes       |               |
| `MAINTENANCE__MAINTENANCE_PATH`                 | The path to the `json` file containing the maintenance state.                                                             | Yes       |               |
| `MAINTENANCE__SCHEDULED_MAINTENANCE_PATH`       | The path to the `json` file containing the scheduled maintenance state.                                                   | Yes       |               |
| `ICAT_SERVER__URL`                              | The URL to the ICAT server to connect to.                                                                                 | Yes       |               |
| `ICAT_SERVER__CERTIFICATE_VALIDATION`           | Whether to verify ICAT certificates using its internal trust store or disable certificate validation completely.          | Yes       |               |
| `ICAT_SERVER__REQUEST_TIMEOUT_SECONDS`          | The maximum number of seconds that the request should wait for a response from ICAT before timing out.                    | Yes       |               |

### How to add or remove a JWT refresh token from the blacklist

The `AUTHENTICATION__JWT_REFRESH_TOKEN_BLACKLIST` environment variable holds the list of blacklisted JWT refresh tokens
which when received will reject to refresh the provided access token. This means that you can add or remove a JWT
refresh token from the blacklist by adding or removing the token from the environment variable.

**PLEASE NOTE** Changes made to the `AUTHENTICATION__JWT_REFRESH_TOKEN_BLACKLIST` environment variable require the
application/container to be restarted in order for them to take effect. This is because the values for the environment
variable gets loaded once at startup.

### How to update maintenance or scheduled maintenance state

The `maintenance` folder at the root of the project directory contains two json files which return the appropriate state
of the system. This means that you can edit the values in the files in accordance with the desired state of the system.

**_PLEASE NOTE_** Changes made to `maintenance.json` and `scheduled_maintenance.json` file using vim do not get synced
in the Docker container because it changes the inode index number of the file. A workaround is to create a new file
using the `maintenance.json` or `scheduled_maintenance.json` file, apply your changes in the new file, and then
overwrite the `maintenance.json` / `scheduled_maintenance.json` file with the content of the new file, see below an
example for `maintenance.json` file.

```bash
cp maintenance/maintenance.json new_maintenance.json
vim new_maintenance.json
cat new_maintenance.json > maintenance/maintenance.json
rm new_maintenance.json
```

### Nox Sessions

This repository contains a [Nox](https://nox.thea.codes) file (`noxfile.py`) which exists in the root level of this
repository. There are a handful of sessions which help with repetitive tasks during development. To install Nox, use the
following command:

```bash
pip install --user --upgrade nox
```

To run a specific Nox session, use the following:

```bash
nox -s [SESSION NAME]
```

Currently, the following Nox sessions have been created:
- `black` - this uses [Black](https://black.readthedocs.io/en/stable/) to format Python code to a pre-defined style.
- `lint` - this uses [flake8](https://flake8.pycqa.org/en/latest/) with a number of additional plugins (see the
  included`noxfile.py` to see which plugins are used) to lint the code to keep it Pythonic. `.flake8` configures
  `flake8` and the plugins.
- `safety` - this uses [safety](https://github.com/pyupio/safety) to check the dependencies (pulled directly from
  Poetry) for any known vulnerabilities. This session gives the output in a full ASCII style report.
- `tests` - this uses [pytest](https://docs.pytest.org/en/stable/) to execute the automated tests in `test/`.

### Automated Checks during Git Commit (Pre Commit)

To make use of Git's ability to run custom hooks, [pre-commit](https://pre-commit.com/) is used. Pip is used to install
this tool:

```bash
pip install --user --upgrade pre-commit
```

This repo contains an existing config file for `pre-commit` (`.pre-commit-config.yaml`) which needs to be installed
using:

```bash
pre-commit install
```

When you commit work on this repo, the configured commit hooks will be executed, but only on the changed files. This is
good because it keeps the process of committing a simple one, but to run the hooks on all the files locally, execute the
following command:

```bash
pre-commit run --all-files
```
