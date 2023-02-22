# Virga


## Authenticating with GCloud

Projects generated with `--auth` require GCR access to download and run the Noct service, Indico's platform-wide authentication server. To setup GCR access on your machine:

1. Download the `gcr` service account key file provided by an Indico admin (check with your employee contact or DevOps).
2. Download the Google Cloud SDK (<https://cloud.google.com/sdk/docs/install>).
3. Authenticate with the provided service account key: `gcloud auth activate-service-account --key-file=/path/to/key.json`.
4. Configure Docker to run with GCR: `gcloud auth configure-docker`.

## Generating an app

Virga applications, and Virga itself, are [Poetry](https://python-poetry.org/) projects; they use Poetry as a python dependency and virtual environment manager. To install Poetry, follow the [instructions on its documentation site](https://python-poetry.org/docs/).

In order to create an app with a UI, you must also install [Yarn](https://yarnpkg.com/getting-started/install).

### 1. Install Poetry and Yarn (assumes Python >= 3.7):

  ```sh
  curl -sSL https://install.python-poetry.org | python3 -
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt-get install -y nodejs
  npm install --global yarn
  ```

### 2. Generate a new project:

  **For now, Virga is not publically published. To run Virga commands, you must pip install it from this repo rather than PyPI.**

  ```sh
  python -m pip install "virga[cli] @ git+https://github.com/IndicoDataSolutions/virga.git"
  ```

  You can create a new project by running `virga new <NAME> [FLAGS]`. This command will generate a new project with the given flags. General command usage and descriptions of avaliable flags are available with `virga new --help`.

  See [plugin dependencies](#Plugin-dependencies) for some caveats.

### 3. Development and Testing

When you generate a Virga project, you'll have an `api` subdirectory and (optionally) a `webui` subdirectory. They represent the backend and frontend of a self-container sidecar application. As such, it's likely that you will want to test integration to make sure each end responds and requests correctly to the other.

The `docker-compose` files that are generated with a project are setup specifically to enable easier integration testing. **The API Dockerfile is production-ready, but all other Docker-related files are not meant for production use.** When you spin up the root `docker-compose` file, the front-end and back-end will each spin up a server in separate development containers, with hot reloading enabled on both, connected by a third container running Caddy 2. Caddy 2 is an HTTP server that will listen to incoming requests and proxy them to the UI and API containers, with the API mounted on `/api` and the UI being `/`.

To make sure you can access the Caddy container from your machine, you will need to add `APP_NAME.indico.local` to your local hosts file (`/etc/hosts` on most Linux systems):

  - Find the running app container IP by running `docker inspect APP_NAME_caddy_1 | grep "IPAddress" | tail -1 | awk -F[\"\"] '{print $4}'`
  - Add `IP_ADDRESS APP_NAME.indico.local` to your hosts file.

Then you can `docker-compose up` from the root directory.

You should be able to access the UI at `https://APP_NAME.indico.local` and the API at `https://APP_NAME.indico.local/api`. If Noct is enabled, you should also be able to verify it is running by going to `https://APP_NAME.indico.local/auth/api/ping`.

## Plugin dependencies

As of 1.2, Virga makes an attempt to have generated projects require as few dependencies as possible, to avoid unnecessarily large footprints. This means that the dependencies that the `noct`, `database`, and `graphql` plugins require have been moved to optional extras, and are conditionally added to your project during generation based on the configuration options provided during generation.

If you generate a project without explicitly using an option, and then try to use its corresponding plugin, your application will fail with a message indicating you're missing the required extra(s). To resolve that issue, edit your API's `pyproject.toml` to include the extra(s) you need:

```toml
# before
virga = {
  git = "https://github.com/IndicoDataSolutions/virga.git", rev = "main"
}

# after, assuming you want to include all the extras
virga = {
  git = "https://github.com/IndicoDataSolutions/virga.git", rev = "main",
  extras = ["auth", "graphql", "database"]
}
```

You'll need to re-run `poetry update` to have the updates reflected.

The available extras are:

- `auth` for the Noct plugin, which adds `python-jose` and `aiohttp`.
- `database` for the database plugin, which adds `SQLAlchemy`, `asyncpg`, and `alembic`.
- `graphql` for the GraphQL plugin, which adds `graphene`, `aiofiles`, and `aiodataloader`.


## Authenticated routes

For now, all routes are unauthenticated unless explicitly required. Authentication and requests for the current user can be added to a route via FastAPI's [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/?h=depends) system. In general, adding

```python
current_user: User = Depends(get_current_user)
```

to any route's definition will force it to require authentication. For example:

```python
from virga.plugins.noct import User, get_current_user

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

## Database connections

Like with authentication, all routes needing access to a database connection must explicitly ask for one through a route dependency. Adding

```python
session: AsyncSession = Depends(async_session)
```

to any route's definition will automatically open and close an asynchronous database connection. An example is provided in all generated sidecar applications.

### Alembic

Virga's `--database` option provides a baseline structure for managing database schema and migrations through Alembic. Detailed instructions about generating and running database migrations are available on its [documentation website](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script).

## GraphQL that requires the DB or authentication

The base `GraphQLRoute` provided by Virga does not implement any method for checking authentication or supplying a database connection to downstream resolvers. If your API requires this, use a `SessionedGraphQLRoute` instead.

SessionedGraphQLRoute accepts two kwargs, `database_url` and `authenticated`. When `authenticted` is True, the route will check the request authentication cookies, exactly like `get_current_user`, and if valid will attach `user` and `token` fields to the GQL context passed to resolvers. - When `database_url` is set, it will be used to start an async db session that will be attached to the GQL context via the `db_session` field.

For example:

```python
schema = Schema(query=RootQuery)

# this for no authentication or database access
# it is equivalent to using GraphQLRoute
app.add_route("/graphql", SessionedGraphQLRoute(schema=schema))

# this for authentication
app.add_route(
  "/graphql",
  SessionedGraphQLRoute(schema=schema, authenticated=True)
)

# this for database access
app.add_route(
  "/graphql",
  SessionedGraphQLRoute(schema=schema, database_url=settings().db_url)
)
```
