FROM python:3.7-slim-buster

COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /start-reload.sh /start-reload.sh
COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /start.sh /start.sh
COPY --from=tiangolo/uvicorn-gunicorn:python3.7 /gunicorn_conf.py /gunicorn_conf.py

# configure env vars for runtime
ENV APP_NAME=review_list_page-api \
    APP_MODULE="review_list_page.app:app" \
    API_PORT=5000 \
    ACCESS_LOG="/var/log/review_list_page-api.log" \
    PRE_START_PATH="/review_list_page-api/scripts/prestart.sh" \
    POETRY_HOME=/etc/poetry
ENV PORT=${API_PORT} ERROR_LOG="${ACCESS_LOG}" PATH="${PATH}:${POETRY_HOME}/bin"

# install system dependencies and poetry
RUN apt update && \
    apt install -y curl vim postgresql-client git && \
    apt autoremove -y && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - && \
    chmod 755 ${POETRY_HOME}/bin/poetry && \
    . ${POETRY_HOME}/env && \
    poetry config virtualenvs.create false

# copy everything and install app dependencies
COPY . /review_list_page-api
WORKDIR /review_list_page-api
RUN poetry install --remove-untracked --no-interaction

# launch the service
EXPOSE $API_PORT
CMD [ "/review_list_page-api/scripts/entrypoint.sh" ]
