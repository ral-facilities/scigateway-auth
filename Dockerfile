# This is the Dockerfile for the Scigateway_auth container

FROM python:3.7

# install dependancies
RUN pip install poetry
RUN apt-get update && apt-get install -y openssh-client

WORKDIR /app

# make dir to hold keys
RUN mkdir keys

# copy code across
COPY . /app

# install app dependancies
RUN poetry config virtualenvs.create false
RUN poetry install
RUN ssh-keygen -q -t rsa -m 'PEM' -N '' -f keys/jwt-key

# set the app running
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["python3", "-m", "scigateway_auth.app"]