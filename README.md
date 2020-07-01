# scigateway-auth

Authentication API for the SciGateway web application

## Contents

- [scigateway-auth](#scigateway-auth)
  - [Contents](#contents)
  - [Requirements](#requirements)
  - [Setup and running the API](#setup-and-running-the-api)
  - [Project structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Viewing Swagger Documentation](#viewing-swagger-documentation)

## Requirements

All requirements can be installed with `pip install -r requirements.txt`

## Setup and running the API

To run the application, you must first create a `config.json` in the same level as `config.json.example`. You then need to generate a public/private key pair for the application to use to sign its JWTs. Running `ssh-keygen -t rsa -m 'PEM'` and creating passwordless keys should work. By default, the keys are expected to be in `keys/` with the names `jwt-key` and `jwt-key.pub` - however the paths to the private and public keys can be configured in `config.json`. There are example keys used for tests in `test/keys/`.

Then the api may be started by using `python app.py`

The `verify` option in `config.json` corresponds to what is supplied to the [`request`](https://requests.readthedocs.io/en/master/) calls to the ICAT server. This can be set to multiple different values:

- `true`: This sets `verify=True` and means that `requests` will verify certificates using it's internal trust store (note: this is not the same as the system trust store). In practice this means only "real" signed certificates will be verified. This is useful for production.
- `false`: This sets `verify=False` and thus disables certificate verification. This is useful for dev but should not be used in production.
- `"/path/to/CA_BUNDLE"`: this sets `verify="/path/to/CA_BUNDLE"` and will allow you to explicitly trust _only_ the specified self signed certificate. This is useful for preprod or production.

## Project structure

The project consists of 3 main packages, and app.py. The config, constants and exceptions are in the `common` package and the endpoints and authentication logic are in `src`. The api is setup in app.py. A directory tree is shown below:

```
─── scigateway-auth
    ├── app.py
    ├── common
    │   ├── config.py
    │   ├── constants.py
    │   ├── exceptions.py
    │   └── logger_setup.py
    ├── src
    │   ├── auth.py
    │   └── endpoints.py
    │── test
    │   ├── test_authenticationHandler.py
    │   ├── test_ICATAuthenticator.py
    │   └── test_requires_mnemonic.py
    ├── config.json
    ├── logs.log
    ├── openapi.yaml
    ├── README.md
    └── requirements.txt
```

## Running Tests

When in the base directory of this repo, use `python -m unittest discover` to run the unit tests located in `test/`.

## Viewing Swagger Documentation

In the base directory of this repository, there's a file called `openapi.yaml`. This follows OpenAPI specifcations to display how this API is implemented, using a technology called [Swagger](https://swagger.io/). Go to https://petstore.swagger.io/ and using the text field at the top of the page, paste the link to the raw YAML file inside this repo. Click the explore button to see example snippets of how to use the API. This can be useful to see the valid syntax of the request body's of the POST requests.
