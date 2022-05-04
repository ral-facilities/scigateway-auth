# Dockerfile to build and serve scigateway-auth

FROM python:3.6-alpine3.15

WORKDIR /scigateway-auth

COPY . .

RUN python -m pip install --upgrade pip
# Install the dependency management tool
RUN pip install poetry

RUN poetry config virtualenvs.create false
# TODO - Should this be added to the existing pyproject.toml of the repo?
# This way, dependabot can take care of updates.
RUN poetry add gunicorn=^20.1.0
RUN poetry install --no-dev

# Generate JWT keys
RUN mkdir keys
RUN ssh-keygen -t rsa -m 'PEM' -f keys/jwt-key

# Serve the application using gunicorn - production ready WSGI server
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py", "scigateway_auth.wsgi:application"]
