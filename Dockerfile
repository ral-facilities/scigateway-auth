# Dockerfile to build and serve scigateway-auth

# Build stage
FROM python:3.11-alpine3.17 as builder

WORKDIR /scigateway-auth-build

COPY README.md poetry.lock pyproject.toml ./
COPY scigateway_auth/ scigateway_auth/

RUN --mount=type=cache,target=/root/.cache \
    set -eux; \
    \
    python3 -m pip install 'poetry~=1.3.2'; \
    poetry build;


# Install & run stage
FROM python:3.11-alpine3.17

WORKDIR /scigateway-auth-run

COPY --from=builder /scigateway-auth-build/dist/scigateway_auth-*.whl /tmp/
COPY maintenance/ maintenance/

RUN --mount=type=cache,target=/root/.cache \
    set -eux; \
    \
    apk add --no-cache openssh-keygen; \
    python3 -m pip install \
        'gunicorn~=20.1.0' \
        /tmp/scigateway_auth-*.whl; \
    \
    SCIGATEWAY_AUTH_LOCATION="$(python3 -m pip show scigateway_auth | awk '/^Location:/ { print $2 }')"; \
    \
    # Create config.json from its .example file. It will need to be editted by the entrypoint script so create it in our non-root user's home directory and create a symlink \
    cp "$SCIGATEWAY_AUTH_LOCATION/scigateway_auth/config.json.example" /scigateway-auth-run/config.json; \
    ln -s /scigateway-auth-run/config.json "$SCIGATEWAY_AUTH_LOCATION/scigateway_auth/config.json"; \
    \
    # Create directory for JWT keys (they will be generated in the entrypoint script) \
    mkdir /scigateway-auth-run/keys; \
    chmod 0700 /scigateway-auth-run/keys; \
    \
    # Create a non-root user to run as \
    addgroup -S scigateway-auth; \
    adduser -S -D -G scigateway-auth -H -h /scigateway-auth-run scigateway-auth; \
    chown -R scigateway-auth:scigateway-auth /scigateway-auth-run;

USER scigateway-auth

ENV ICAT_URL="http://localhost"
ENV LOG_LOCATION="/dev/stdout"
ENV PRIVATE_KEY_PATH="/scigateway-auth-run/keys/jwt-key"
ENV PUBLIC_KEY_PATH="/scigateway-auth-run/keys/jwt-key.pub"
ENV MAINTENANCE_CONFIG_PATH="/scigateway-auth-run/maintenance/maintenance.json"
ENV SCHEDULED_MAINTENANCE_CONFIG_PATH="/scigateway-auth-run/maintenance/scheduled_maintenance.json"
ENV VERIFY="true"

COPY docker/docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

# Serve the application using gunicorn - production ready WSGI server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "scigateway_auth.wsgi"]
EXPOSE 8000
