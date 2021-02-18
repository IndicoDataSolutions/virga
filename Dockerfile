FROM gcr.io/new-indico/ubuntu:18.04

ENV APP_NAME virga
ENV POETRY_HOME=/etc/poetry

# system dependencies
RUN apt update && \
    apt install -y python3.8-dev

COPY . /virga
WORKDIR /virga

# app dependencies
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - && \
    . /etc/poetry/env && \
    poetry install --remove-untracked

ENTRYPOINT "/virga/scripts/entrypoint.sh"
