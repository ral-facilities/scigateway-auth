FROM python:3.13-alpine3.24@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741 AS base

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache \
    set -eux; \
    \
    pip install --no-cache-dir 'poetry==2.5.1' poetry-plugin-export; \
    \
    poetry export --only dev --format requirements.txt --without-hashes --output requirements-dev.txt; \
    poetry export --without dev --format requirements.txt --without-hashes --output requirements-prod.txt;


FROM python:3.13-alpine3.24@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741 AS dev

WORKDIR /app

COPY --from=base /app/requirements-*.txt ./
COPY poetry.lock pyproject.toml .flake8 ./
COPY scigateway_auth/ scigateway_auth/
COPY maintenance/ maintenance/

RUN --mount=type=cache,target=/root/.cache \
    set -eux; \
    \
    apk add --no-cache gcc musl-dev linux-headers python3-dev; \
    \
    pip install --no-cache-dir --requirement requirements-dev.txt --requirement requirements-prod.txt;

CMD ["fastapi", "dev", "scigateway_auth/main.py", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000


FROM dev as test

WORKDIR /app

COPY test/ test/

CMD ["pytest",  "--config-file", "test/pytest.ini", "--cov", "scigateway_auth", "--cov-report", "term-missing", "-v"]


FROM python:3.13-alpine3.24@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741 AS prod

WORKDIR /app

COPY --from=base /app/requirements-prod.txt ./
COPY scigateway_auth/ scigateway_auth/

RUN --mount=type=cache,target=/root/.cache \
    set -eux; \
    \
    pip install --no-cache-dir --requirement requirements-prod.txt; \
    \
    # Create a non-root user to run as \
    addgroup -g 500 -S scigateway-auth; \
    adduser -S -D -G scigateway-auth -H -u 500 -h /app scigateway-auth;

USER scigateway-auth

CMD ["fastapi", "run", "scigateway_auth/main.py", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
