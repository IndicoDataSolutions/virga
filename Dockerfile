FROM python:3.8-slim

ENV APP_NAME=virga POETRY_HOME=/etc/poetry
ENV PATH = "${PATH}:/etc/poetry/bin"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -yf --no-install-suggests --no-install-recommends \
        build-essential curl vim git && \
    # node
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash && \
    apt install --no-install-recommends -y nodejs && \
    apt-get install -yf --no-install-suggests --no-install-recommends \
        nodejs npm && \
    npm install -g yarn && \
    # helm
    curl -fsSL \
        https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /virga
WORKDIR /virga

# python dependencies (Poetry)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false && \
    poetry install --all-extras

CMD [ "bash" ]
