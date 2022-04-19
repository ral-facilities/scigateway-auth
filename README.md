[![Build Status](https://github.com/ral-facilities/scigateway-auth/workflows/CI/badge.svg?branch=main)](https://github.com/ral-facilities/scigateway-auth/actions?query=workflow%3A%22CI%22)
[![Codecov](https://codecov.io/gh/ral-facilities/scigateway-auth/branch/main/graph/badge.svg)](https://codecov.io/gh/ral-facilities/scigateway-auth)

# scigateway-auth

Authentication API for the SciGateway web application

## Contents

- [scigateway-auth](#scigateway-auth)
  - [Contents](#contents)
- [Creating Dev Environment and API Setup](#creating-dev-environment-and-api-setup)
  - [Python Version Management (pyenv)](#python-version-management-pyenv)
  - [API Dependency Management (Poetry)](#api-dependency-management-poetry)
  - [Automated Testing & Other Development Helpers (Nox)](#automated-testing--other-development-helpers-nox)
  - [Automated Checks during Git Commit (Pre Commit)](#automated-checks-during-git-commit-pre-commit)
  - [Summary](#summary)
- [Running the API](#running-the-api)
- [Project structure](#project-structure)
- [Running Tests](#running-tests)
- [Viewing Swagger Documentation](#viewing-swagger-documentation)

# Creating Dev Environment and API Setup
The recommended development environment for this API has taken lots of inspiration from
the [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
guide found online. It is assumed the commands shown in this part of the README are
executed in the root directory of this repo once it has been cloned to your local
machine.

## Python Version Management (pyenv)
To start, install [pyenv](https://github.com/pyenv/pyenv). There is a Windows version of
this tool ([pyenv-win](https://github.com/pyenv-win/pyenv-win)), however this is
currently untested on this repo. This is used to manage the various versions of Python
that will be used to test/lint Python during development. Install by executing the
following:

```bash
curl https://pyenv.run | bash
```

The following lines need to be added to `~/.bashrc` - either open a new terminal or
execute `source ~/.bashrc` to make these changes apply:

```bash
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Various Python build dependencies need to be installed next. These will vary dependent
on the platform of your system (see the
[common pyenv build problems](https://github.com/pyenv/pyenv/wiki/Common-build-problems)
for the relevant command for your OS), but the following shows the bash command to
install the requirements for a CentOS/RHEL machine:

```bash
sudo yum install @development zlib-devel bzip2 bzip2-devel readline-devel sqlite \
sqlite-devel openssl-devel xz xz-devel libffi-devel findutils
```

To make use of `pyenv`, let's install different versions of Python onto the system. In
production, SciGateway Auth uses Python 3.6, so this should definitely be part a
development environment for this repo. This stage might take some time as each Python
version needs to be downloaded and built individually:

```bash
pyenv install 3.6.8
pyenv install 3.7.7
pyenv install 3.8.2
pyenv install 3.9.0
```

To verify the installation commands worked:

```bash
python3.6 --version
python3.7 --version
python3.8 --version
python3.9 --version
```

These Python versions need to be made available to local version of the repository. They
will used during the Nox sessions, explained further down this file. Executing the
following command will create a `.python-version` file inside the repo (this file is
currently listed in `.gitignore`):

```bash
pyenv local 3.6.8 3.7.7 3.8.2 3.9.0
```

## API Dependency Management (Poetry)
To maintain records of the API's dependencies,
[Poetry](https://github.com/python-poetry/poetry) is used. To install, use the following
command:

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

The installation requires `~/.poetry/env` to be refreshed for changes to be applied.
Open a new terminal or execute the following command to ensure the installation is
completed smoothly:

```bash
source ~/.poetry/env
```

The dependencies for this repo are stored in `pyproject.toml`, with a more detailed
version of this data in `poetry.lock`. The lock file is used to maintain the exact
versions of dependencies from system to system. To install the dependencies, execute the
following command (add `--no-dev` if you don't want the dev dependencies):

```bash
poetry install
```

To add a dependency to Poetry, run the following command (add `--dev` if it's a
development related dependency). The
[official docs](https://python-poetry.org/docs/cli/#add) give good detail regarding the
intricacies of this command:

```bash
poetry add [PACKAGE-NAME]
```

## Automated Testing & Other Development Helpers (Nox)
When developing new features for the API, there are a number of Nox sessions that can be
used to lint/format/test the code in the included `noxfile.py`. To install Nox, use Pip
as shown below. Nox is not listed as a Poetry dependency because this has the potential
to cause issues if Nox was executed inside Poetry (see
[here](https://medium.com/@cjolowicz/nox-is-a-part-of-your-global-developer-environment-like-poetry-pre-commit-pyenv-or-pipx-1cdeba9198bd)
for more detailed reasoning). When using the `--user` option, ensure your user's Python
installation is added to the system `PATH` variable, remembering to reboot your system
if you need to change the `PATH`. If you do choose to install these packages within a
virtual environment, you do not need the `--user` option:

```bash
pip install --user --upgrade nox
```

To run the sessions defined in `nox.options.sessions` (see `noxfile.py`), simply run:

```bash
nox
```

To execute a specific nox session, the following will do that:

```bash
nox -s [SESSION/FUNCTION NAME]
```

Currently, the following Nox sessions have been created:
- `black` - this uses [Black](https://black.readthedocs.io/en/stable/) to format Python
  code to a pre-defined style.
- `lint` - this uses [flake8](https://flake8.pycqa.org/en/latest/) with a number of
  additional plugins (see the included `noxfile.py` to see which plugins are used) to
  lint the code to keep it Pythonic. `.flake8` configures `flake8` and the plugins.
- `safety` - this uses [safety](https://github.com/pyupio/safety) to check the
  dependencies (pulled directly from Poetry) for any known vulnerabilities. This session
  gives the output in a full ASCII style report.
- `tests` - this uses [pytest](https://docs.pytest.org/en/stable/) to execute the
  automated tests in `test/`, tests for the database and ICAT backends, and non-backend
  specific tests. More details about the tests themselves [here](#running-tests).

Each Nox session builds an environment using the repo's dependencies (defined using
Poetry) using `install_with_constraints()`. This stores the dependencies in a
`requirements.txt`-like format temporarily during this process, using the OS' default
temporary location. These files are manually deleted in `noxfile.py` (as opposed to
being automatically removed by Python) to minimise any potential permission-related
issues as documented
[here](https://github.com/bravoserver/bravo/issues/111#issuecomment-826990).

## Automated Checks during Git Commit (Pre Commit)
To make use of Git's ability to run custom hooks, [pre-commit](https://pre-commit.com/)
is used. Like Nox, Pip is used to install this tool:

```bash
pip install --user --upgrade pre-commit
```

This repo contains an existing config file for `pre-commit` (`.pre-commit-config.yaml`)
which needs to be installed using:

```bash
pre-commit install
```

When you commit work on this repo, the configured commit hooks will be executed, but
only on the changed files. This is good because it keeps the process of committing
a simple one, but to run the hooks on all the files locally, execute the following
command:

```bash
pre-commit run --all-files
```

## Summary
As a summary, these are the steps needed to create a dev environment for this repo
compressed into a single code block:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Paste into ~/.bashrc
export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Apply changes made in ~/.bashrc
source ~/.bashrc

# Install Python build tools
sudo yum install @development zlib-devel bzip2 bzip2-devel readline-devel sqlite \
sqlite-devel openssl-devel xz xz-devel libffi-devel findutils

# Install different versions of Python and verify they work
pyenv install 3.6.8
python3.6 --version
pyenv install 3.7.7
python3.7 --version
pyenv install 3.8.2
python3.8 --version
pyenv install 3.9.0
python3.9 --version

# Make installed Python versions available to repo
pyenv local 3.6.8 3.7.7 3.8.2 3.9.0

# Install Poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Apply changes made to file when installing Poetry
source ~/.poetry/env

# Install API's dependencies
poetry install

# Install Nox
pip install --user --upgrade nox

# Install Pre Commit
pip install --user --upgrade pre-commit

# Install commit hooks
pre-commit install
```


# Running the API

To run the application, you must first create a `config.json` in the same level as `config.json.example`. You then need to generate a public/private key pair for the application to use to sign its JWTs. Running `ssh-keygen -t rsa -m 'PEM'` and creating passwordless keys should work. By default, the keys are expected to be in `keys/` with the names `jwt-key` and `jwt-key.pub` - however the paths to the private and public keys can be configured in `config.json`. There are example keys used for tests in `test/keys/`.

Then the api may be started by using `python3 -m scigateway_auth.app`

The `verify` option in `config.json` corresponds to what is supplied to the [`request`](https://requests.readthedocs.io/en/master/) calls to the ICAT server. This can be set to multiple different values:

- `true`: This sets `verify=True` and means that `requests` will verify certificates using it's internal trust store (note: this is not the same as the system trust store). In practice this means only "real" signed certificates will be verified. This is useful for production.
- `false`: This sets `verify=False` and thus disables certificate verification. This is useful for dev but should not be used in production.
- `"/path/to/CA_BUNDLE"`: this sets `verify="/path/to/CA_BUNDLE"` and will allow you to explicitly trust _only_ the specified self signed certificate. This is useful for preprod or production.

# Project structure

The project consists of 3 main packages, and app.py. The config, constants and exceptions are in the `common` package and the endpoints and authentication logic are in `src`. The api is setup in app.py. A directory tree is shown below:

```
─── scigateway-auth
    ├── scigateway_auth
    │   ├── app.py
    │   ├── wsgi.py
    │   ├── common
    │   │   ├── config.py
    │   │   ├── constants.py
    │   │   ├── exceptions.py
    │   │   └── logger_setup.py
    │   ├── src
    │   │   ├── auth.py
    │   │   └── endpoints.py
    │   └── config.json
    ├── test
    │   ├── test_authenticationHandler.py
    │   ├── test_ICATAuthenticator.py
    │   └── test_requires_mnemonic.py
    ├── logs.log
    ├── noxfile.py
    ├── openapi.yaml
    ├── poetry.lock
    ├── pyproject.toml
    └── README.md
```

# Running Tests

When in the base directory of this repo, use `nox -s tests` to run the unit tests located in `test/`.

# Viewing Swagger Documentation

In the base directory of this repository, there's a file called `openapi.yaml`. This follows OpenAPI specifcations to display how this API is implemented, using a technology called [Swagger](https://swagger.io/). Go to https://petstore.swagger.io/ and using the text field at the top of the page, paste the link to the raw YAML file inside this repo. Click the explore button to see example snippets of how to use the API. This can be useful to see the valid syntax of the request body's of the POST requests.
