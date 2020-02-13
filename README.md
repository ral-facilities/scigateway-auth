# scigateway-auth

Authentication API for the SciGateway web application

## Contents

- [scigateway-auth](#scigateway-auth)

  - [Contents](#contents)
  - [Requirements](#requirements)
  - [Setup and running the API](#setup-and-running-the-api)
  - [Project structure](#project-structure)
  - [Running Tests](#running-tests)

## Requirements

All requirements can be installed with `pip install -r requirements.txt`

## Setup and running the API

To run the application, you must first create a `config.json` in the same level as `config.json.example`.
Then the api may be ran by using `python scigateway-auth/app.py`

The `verify` option in `config.json` corresponds to what is supplied to the [`request`](https://requests.readthedocs.io/en/master/) calls to the ICAT server. This can be set to multiple different values:

- `true`: This sets `verify=True` and means that `requests` will verify certificates using it's internal trust store (note: this is not the same as the system trust store). In practice this means only "real" signed certificates will be verified. This is useful for production.
- `false`: This sets `verify=False` and thus disables certificate verification. This is useful for dev but should not be used in production.
- `"/path/to/CA_BUNDLE"`: this sets `verify="/path/to/CA_BUNDLE"` and will allow you to explicitly trust _only_ the specified self signed certificate. This is useful for preprod or production.

## Project structure

The project consists of 2 main packages, and app.py. The config, constants and exceptions are in the common
package and the endpoints and authentication logic are in src. The api is setup in app.py. A directory tree
is shown below

```
─── scigateway-auth
    ├── scigateway-auth
    │   ├── common
    │   │   ├── config.py
    │   │   ├── constants.py
    │   │   └── exceptions.py
    │   ├── src
    │   │   ├── auth.py
    │   │   └── endpoints.py
    │   ├── test
    │   └── app.py
    ├── config.json
    ├── README.md
    ├── requirements.in
    └── requirements.txt
```

## Running Tests

To run the tests use `python -m unittest discover`
