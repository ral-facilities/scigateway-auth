# Dockerfile to build and serve scigateway-auth

FROM python:3.6-slim-bullseye

WORKDIR /scigateway-auth

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --upgrade pip \
  && pip install 'poetry==1.1.13' \
  && poetry run pip install 'gunicorn==20.1.0' \
  && poetry install --no-dev \
  && apt-get update \
  && apt-get install -y --no-install-recommends openssh-client \
  && mkdir keys \
  # Generate JWT keys
  && ssh-keygen  -t rsa -m 'PEM' -f keys/jwt-key \
  # Delete the openssh-client package as it is no longer needed
  && rm -rf /var/lib/apt/lists/*

COPY scigateway_auth ./scigateway_auth

# Serve the application using gunicorn - production ready WSGI server
ENTRYPOINT ["poetry", "run", "gunicorn", "-c", "gunicorn.conf.py", "scigateway_auth.wsgi:application"]
