# virga

Templated adaptable sidecar app generation.

## Prerequisites

Virga is a [Poetry](https://python-poetry.org/) project, meaning it uses Poetry as a python dependency and virtual environment manager. To install Poetry, follow the [instructions on its documentation site](https://python-poetry.org/docs/):

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

## Environment

To setup the project, install Poetry dependencies by cloning the repo and running `poetry install` in the project directory:

```sh
git clone git@github.com:IndicoDataSolutions/virga.git
cd virga && poetry install
```

### Testing

You can create a new project by running `virga new test_app --webui --graphql --auth`. This command will generate the new project with the given flags. General command usage is available with `virga --help`.

To test the generated project:

```sh
cd test_app
./run.sh
```

You'll be able to access the UI at `https://app.indico.local`. You can verify noct is running by going to `https://app.indico.local/auth/api/ping`. The templated FastAPI application is mounted to `https://app.indico.local/api`, but it will fail if there are missing python dependencies (if Virga is inaccessible by PyPi, for example).

To test the FastAPI app, omit the `--graphql --auth` flags during generation, and return to `https://app.indico.local/api`. A JSON message should be displayed reading `"Hello World!"`.

> _**NOTE:**_
>
> `./run.sh` is a convience script for spawning the test project inside several Docker containers managed by Docker Compose. Depending on the flags used to generate the application, different services will be created.
>
> In order for the hostname DNS resolution to succeed, `./run.sh` spawns a [DNS Proxy Server](https://mageddo.github.io/dns-proxy-server/latest/en/), which allows the container hostnames to resolve on the host machine without knowing the container IPs. Due to proxy restrictions, some existing services might not function correctly (namly, `gcloud` and `indico-deployment` actions may fail).

### Docker Compose

Virga comes with a `docker-compose` file to make testing easier. Simply `docker-compose up --build`. The Docker setup contains a development version of Noct running an PostgreSQL 9.6.x server running on Alpine, reachable at `http://noct:5000` and `http://noct-db:5432` respectivly.

You can also run the Virga CLI from your host machine by executing through Poetry `poetry run` or via a Poetry shell:

```sh
$ poetry shell
Spawning shell within ~/.cache/pypoetry/virtualenvs/virga-4k78GcwH-py3.8
(virga-4k78GcwH-py3.8) $ 
```
