FROM python:3.7-slim-buster

ENV APP_NAME=virga POETRY_HOME=/etc/poetry

RUN apt update && \
    apt install -y curl vim git && \
    curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt install -y nodejs && \
    npm install -g yarn

COPY . /virga
WORKDIR /virga

# python dependencies (Poetry)
RUN pip3 install --upgrade pip && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - && \
    . /etc/poetry/env && \
    poetry config virtualenvs.create false && \
    poetry install

ENV PATH = "${PATH}:/etc/poetry/bin"

CMD [ "tail", "-f", "/dev/null" ]