# Dockerfile to build and serve scigateway-auth

FROM python:alpine3.15

WORKDIR /scigateway-auth

COPY . .

RUN python -m pip install --upgrade pip
# Install the dependency management tool
RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
