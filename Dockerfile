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
    # Create a symlink to the installed python module \
    SCIGATEWAY_AUTH_LOCATION="$(python3 -m pip show scigateway_auth | awk '/^Location:/ { print $2 }')"; \
    ln -s "$SCIGATEWAY_AUTH_LOCATION/scigateway_auth/" scigateway_auth; \
    \
    # Create config.json from its .example file \
    cp scigateway_auth/config.json.example scigateway_auth/config.json; \
    \
    # Create directory for JWT keys (they will be generated in the entrypoint script) \
    mkdir keys; \
    chmod 0700 keys; \
    \
    # Create a non-root user to run as \
    addgroup -S scigateway-auth; \
    adduser -S -D -G scigateway-auth -H -h /scigateway-auth-run scigateway-auth; \
    \
    # Change ownership of maintenance/ - it needs to be writable at runtime \
    # Change ownership of keys/ and config.json - the entrypoint script will need to edit them \
    chown -R scigateway-auth:scigateway-auth keys/ maintenance/ scigateway_auth/config.json;

USER scigateway-auth

ENV ICAT_URL="http://localhost"
ENV LOG_LOCATION="/dev/stdout"
ENV PRIVATE_KEY_PATH="keys/jwt-key"
ENV PUBLIC_KEY_PATH="keys/jwt-key.pub"
ENV MAINTENANCE_CONFIG_PATH="maintenance/maintenance.json"
ENV SCHEDULED_MAINTENANCE_CONFIG_PATH="maintenance/scheduled_maintenance.json"
ENV VERIFY="true"

COPY docker/docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

# Serve the application using gunicorn - production ready WSGI server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "scigateway_auth.wsgi"]
EXPOSE 8000
