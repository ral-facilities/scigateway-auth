# Dockerfile to build and serve scigateway-auth

FROM python:3.6-slim-bullseye

# Install the openssh-keygen system package as well as the packages
# required to build and install the cryptography dependency with pip 
RUN apk add --no-cache --virtual build-dependencies \
    openssh-keygen

WORKDIR /scigateway-auth

COPY . .

RUN python -m pip install --upgrade pip
# Install the dependency management tool
RUN pip install poetry

RUN poetry config virtualenvs.create false
# TODO - Should this be added to the existing pyproject.toml of the repo?
# This way, dependabot can take care of updates.
RUN poetry run pip install 'gunicorn==20.1.0'
RUN poetry install --no-dev

# Generate JWT keys
RUN mkdir keys
RUN ssh-keygen -t rsa -m 'PEM' -f keys/jwt-key

# Delete the system packages installed earlier as they are no longer needed
RUN apk del build-dependencies

# Serve the application using gunicorn - production ready WSGI server
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py", "scigateway_auth.wsgi:application"]
