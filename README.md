# virga

Templated adaptable sidecar app generation.

## Usage

### Authenticating with GCloud

Projects generated with `--auth` require GCR access to download and run the Noct service, Indico's platform-wide authentication server. To setup GCR access on your machine:

1. Download the `gcr` service account key file from an Indico admin.
2. Download the Google Cloud SDK (<https://cloud.google.com/sdk/docs/install>).
3. Authenticate with the provided service account key: `gcloud auth activate-service-account --key-file=/path/to/key.json`.
4. Configure Docker to run with GCR: `gcloud auth configure-docker`.

### Generating an app

**For now, Virga is not publically released. To run Virga commands, you must clone this repo and run `poetry install`, then `poetry shell`. All commands must be run from within `poetry shell` or via `poetry run`. See the [development section](#development) for more information.**

You can create a new project by running `virga new new_app --webui --graphql --auth`. This command will generate the new project with the given flags. General command usage is available with `virga new --help`.

> Note: To avoid GitHub HTTPS authentication every time a project is generated, set the `GITHUB_ACCESS_TOKEN` to a valid GitHub access token.

---

To launch the generated project:

```sh
cd new_app
./run.sh
```

You'll be able to access the UI at `https://app.indico.local`. You can verify noct is running by going to `https://app.indico.local/auth/api/ping`. The templated FastAPI application is mounted to `https://app.indico.local/api`.

> Note:
>
> `./run.sh` is a convience script for spawning the project inside several Docker containers managed by Docker Compose. Depending on the flags used to generate the application, different services will be created.
>
> In order for the hostname DNS resolution to succeed, `./run.sh` spawns a [DNS proxy server](https://github.com/dvddarias/docker-hoster), which allows the container hostnames to resolve on the host machine without knowing the container IPs. This shouldn't cause any complications since it simply appends and removes entries from your `/etc/hosts` file, but if problems occur, only run the service while testing your generated application.

### Creating a user

As of now, the UI does not support creating users. In order to create a user and access authenticated routes, you must create one manually through the CLI. Noct is responsible for handling users, and there is a convinence script placed within its container's working directory. To create an admin user:

```sh
$ docker exec -it new_project_noct_1 bash
$ python3 alembic/migrations/setup_user_access.py EMAIL_ADDRESS
setup_user_access.py:20: UserWarning: User with email EMAIL_ADDRESS not found, creating...
  warnings.warn("User with email {} not found, creating...".format(email))
Confirm Password for EMAIL_ADDRESS: 
```

### Authenticated routes

For now, all routes are unauthenticated unless explicily required. Authentication and request for the current user can be added to a route via FastAPI's [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/?h=depends) system. In general, adding

```python
current_user: User = Depends(get_current_user)
```

to any route's definition will force it to require authentication. For example:

```python
from virga.types import User
from virga.plugins.noct import get_current_user

# Authenticated by using Virga's `get_current_user` dependency. Access to `/user_info` without
# being logged in will yield a 403 "Login required" error.
@app.get("/user_info")
async def get_user(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}!"}


# Unauthenticated. This route will work regardless of the authentication state of the app.
@app.get("/")
async def read_root():
    return {"msg": "Hello World!"}
```

## Development

Virga is a [Poetry](https://python-poetry.org/) project, meaning it uses Poetry as a python dependency and virtual environment manager. To install Poetry, follow the [instructions on its documentation site](https://python-poetry.org/docs/). To setup the project, install Poetry dependencies by cloning the repo and running `poetry install` in the project directory. Combined, those command will look like the followin:

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
git clone git@github.com:IndicoDataSolutions/virga.git
cd virga && poetry install
```

### Docker Compose

Virga comes with a `docker-compose` file to make testing easier. Simply `docker-compose up --build`. The Docker setup contains a development version of Noct running an PostgreSQL 9.6.x server running on Alpine, reachable at `http://noct:5000` and `http://noct-db:5432` respectivly.

You can also run the Virga CLI from your host machine by executing through Poetry `poetry run` or via a Poetry shell:

```sh
$ poetry shell
Spawning shell within ~/.cache/pypoetry/virtualenvs/virga-4k78GcwH-py3.8
(virga-4k78GcwH-py3.8) $ 
```
