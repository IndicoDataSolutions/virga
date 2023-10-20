FROM python:3.8-slim

ENV APP_NAME=virga POETRY_HOME=/etc/poetry
ENV PATH = "${PATH}:/etc/poetry/bin"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends \
        ca-certificates curl gnupg build-essential curl vim git

# node
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL \
        https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg \
            --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_16.x nodistro main" | tee \
        /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends \
        nodejs npm && \
    npm install -g yarn

# helm
RUN curl -fsSL \
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
