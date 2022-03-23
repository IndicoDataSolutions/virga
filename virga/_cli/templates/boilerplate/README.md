# Virga


## Authenticating with GCloud

Projects generated with `--auth` require GCR access to download and run the Noct service, Indico's platform-wide authentication server. To setup GCR access on your machine:

1. Download the `gcr` service account key file provided by an Indico admin (check with your employee contact or DevOps).
2. Download the Google Cloud SDK (<https://cloud.google.com/sdk/docs/install>).
3. Authenticate with the provided service account key: `gcloud auth activate-service-account --key-file=/path/to/key.json`.
4. Configure Docker to run with GCR: `gcloud auth configure-docker`.

## Generating an app

Virga applications, and Virga itself, are [Poetry](https://python-poetry.org/) projects, meaning they use Poetry as a python dependency and virtual environment manager. To install Poetry, follow the [instructions on its documentation site](https://python-poetry.org/docs/).

In order to create an app with a UI, you must also install [Yarn](https://yarnpkg.com/getting-started/install).

1. Install Poetry and Yarn (assumes Python >= 3.7):

  ```sh
  curl -sSL https://install.python-poetry.org | python3 -
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt-get install -y nodejs
  npm install --global yarn
  ```

2. Generate a new project:

  **For now, Virga is not publically published. To run Virga commands, you must pip install it from this repo rather than PyPI.**

  ```sh
  pip install git+https://github.com/IndicoDataSolutions/virga.git
  ```

  You can create a new project by running `virga new <NAME> [FLAGS]`. This command will generate the new project with the given flags. General command usage and descriptions of avaliable flags are available with `virga new --help`.

3. Launch the generated project:

  ```sh
  docker-compose up # from the project root
  ```

4. Add `APP_NAME.indico.local` to your local hosts file (`/etc/hosts` on most Linux systems)

    - Find the running app container IP by running `docker inspect APP_NAME_caddy_1 | grep "IPAddress" | tail -1 | awk -F[\"\"] '{print $4}'`
    - Add `IP_ADDRESS APP_NAME.indico.local` to your hosts file.

You'll be able to access the UI at `https://APP_NAME.indico.local`. You can verify Noct is running by going to `https://APP_NAME.indico.local/auth/api/ping`. The templated FastAPI application is mounted to `https://APP_NAME.indico.local/api`.

### Creating a user

As of now, the UI does not support creating users. In order to create a user and access authenticated routes, you must create one manually through the CLI. Noct is responsible for handling users, and there is a convenience script placed within its container's working directory. To create an admin user:

```sh
$ docker exec -it new_project_noct_1 bash
$ python3 alembic/migrations/setup_user_access.py EMAIL_ADDRESS
setup_user_access.py:20: UserWarning: User with email EMAIL_ADDRESS not found, creating...
  warnings.warn("User with email {} not found, creating...".format(email))
Confirm Password for EMAIL_ADDRESS: 
Confirm Password for EMAIL_ADDRESS: 
```

### Authenticated routes

For now, all routes are unauthenticated unless explicitly required. Authentication and request for the current user can be added to a route via FastAPI's [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/?h=depends) system. In general, adding

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

You can also add [global dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/) if all your routes will require authentication.

### Database connections

Like with authentication, all routes needing access to a database connection must explicitly ask for one through a route dependency. Adding

```python
session: AsyncSession = Depends(async_session)
```

to any route's definition will automatically open and close an asynchronous database connection. An example is provided in all generated sidecar applications.

#### Alembic

Virga's `--database` option provides a baseline structure for managing database schema and migrations through Alembic. Detailed instructions about generating and running database migrations are available on its [documentation website](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script).

### Docker Compose

Virga comes with a `docker-compose` file to make testing easier. Simply `docker-compose up --build`. The Docker setup contains a development version of Noct running an PostgreSQL 9.6.x server running on Alpine, reachable at `http://noct:5000` and `http://noct-db:5432` respectively.

You can also run the Virga CLI from your host machine by executing through Poetry `poetry run` or via a Poetry shell:

```sh
$ poetry shell
Spawning shell within ~/.cache/pypoetry/virtualenvs/virga-4k78GcwH-py3.8
(virga-4k78GcwH-py3.8) $ 
```
