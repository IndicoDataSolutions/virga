FROM python:3.7-slim-buster

ENV APP_NAME virga
ENV POETRY_HOME=/etc/poetry

RUN apt update && \
    apt install -y curl

COPY . /virga
WORKDIR /virga

# app dependencies
RUN pip3 install --upgrade pip && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - && \
    . /etc/poetry/env && \
    poetry config virtualenvs.create false && \
    poetry install

ENV PATH = "${PATH}:/etc/poetry/bin"

CMD "bash"