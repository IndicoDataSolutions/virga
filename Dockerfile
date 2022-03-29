FROM python:3.7-slim-buster

ENV APP_NAME=virga POETRY_HOME=/etc/poetry
ENV PATH = "${PATH}:/etc/poetry/bin"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential curl vim git && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt install --no-install-recommends -y nodejs && \
    npm install -g yarn && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /virga
WORKDIR /virga

# python dependencies (Poetry)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false && \
    poetry install

CMD ["bash"]