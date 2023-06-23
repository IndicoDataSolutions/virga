# Virga

![virga status](https://img.shields.io/drone/build/IndicoDataSolutions/virga?label=tests&server=https%3A%2F%2Fdrone.devops.indico.io&style=flat-square)

Indico Data's CLI tool for generating sidecar applications. Sidecar apps are not direct parts of Indico's IPA releases, but offer additional or custom functionality for product or business operations.

## Generating an app

Virga applications, and Virga itself, are [Poetry](https://python-poetry.org/) projects; they use Poetry as a python dependency and virtual environment manager. To install Poetry, follow the [instructions on its documentation site](https://python-poetry.org/docs/).

In order to create an app with a UI, you must also install [Yarn](https://yarnpkg.com/getting-started/install).

### 1. Install Poetry and Yarn (assumes Python >= 3.7):

  ```sh
  curl -sSL https://install.python-poetry.org | python3 -
  # if you're going to use --webui
  curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
  sudo apt-get install -y nodejs
  npm install --global yarn
  ```

### 2. Generate a new project:

  **For now, Virga is not publicly published. To run Virga commands, you must pip install it from this repo rather than PyPI.**

  ```sh
  python -m pip install "virga[cli] @ git+https://github.com/IndicoDataSolutions/virga.git"
  ```

  You can create a new project by running `virga new <NAME> [FLAGS]`. This command will generate a new project with the given flags. General command usage and descriptions of available flags are available with `virga new --help`.

  See [plugin dependencies](#Plugin-dependencies) for some caveats.

### 3. Development and Testing

When you generate a Virga project, you'll have an `api` subdirectory and (optionally) a `webui` subdirectory. They represent the backend and frontend of a self-contained sidecar application. As such, it's likely that you will want to test integration to make sure each end responds and requests correctly to the other.

The `docker-compose.yaml` file that is generated with a project is setup specifically to enable easier integration testing. When you spin up the services, the frontend and backend will each spin up a separate development server with hot reloading enabled on both. They'll be connected by a third container running Caddy 2. Caddy 2 is an HTTP web server (like nginx) that will listen to incoming requests and proxy them to the UI and API containers, with the API mounted on `/api` and the UI being `/` of `https://localhost`.

To make testing easier, you might find it valuable to add `APP_NAME.indico.local` to your local hosts file (`/etc/hosts` on most Linux systems):

  - Find the running app container IP by running `docker inspect APP_NAME_caddy_1 | grep "IPAddress" | tail -1 | awk -F[\"\"] '{print $4}'`
  - Add `IP_ADDRESS APP_NAME.indico.local` to your hosts file.
  - Change `localhost` to `APP_NAME.indico.local` at the top of your generated `Caddyfile`.

If you do so, then `docker compose up`, you should be able to access the UI at `https://APP_NAME.indico.local` and the API at `https://APP_NAME.indico.local/api`. If Noct is enabled, you should also be able to verify it is running by going to `https://APP_NAME.indico.local/auth/api/ping`.

If you're using Noct and would like to connect your local environment to an external cluster's authentication, you _will_ have to follow the steps above to update your `/etc/hosts` file. Noct requires that the domain of authentication requests match the domain of the Noct instance, so if you're trying to connect to `customer-dev.indico.domains`, make your local host something like `myapp.customer-dev.indico.domains`.

### 4. Deployment

When creating a Virga application, you have the choice to generate either a standalone deployment or Kubernetes deployment, via either the `--kubernetes` or `--standalone` flags.

#### Kubernetes [the default]

Virga will generate your project assuming a Kubernetes production environment. This means that, in addition to your API (and optional UI), Virga will generate a customizable Helm chart in a top level directory called `charts`. The chart it generates will depend on what other generation flags you specified via the command line, but will always include a `values.yaml` file that highlights your customization options.

In Kubernetes mode, the API assumes that load-balancing happens at the cluster level via something like deployment replicas. As such, the Dockerfile will spin up a single [Uvicorn](https://www.uvicorn.org/) process to react to and respond to requests.

The nginx configuration file will be provided through a Kubernetes volume, allowing more flexible and deployment-specific configuration (like a dynamic `app-config.js`).

Of course, the templates Virga generates are necessarily very generalized. If they're not doing something you need (or are too verbose), you're free to modify them to meet your specific application needs.

#### Standalone

Virga assumes that the project you're creating will be deployed as an independent application outside a managing infrastructure like Kubernetes. No `charts` directory will be generated.

In Standalone mode, the API assumes it must take full responsibility for load-balancing. As such, the Dockerfile will spin up several [Gunicorn](https://gunicorn.org/) workers to handle concurrent requests. The Gunicorn configuration is statically provided by FastAPI's creator, and is available [here](https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/0.7.0/docker-images/gunicorn_conf.py).

## Plugin dependencies

As of 1.2, Virga makes an attempt to have generated projects require as few dependencies as possible, to avoid unnecessarily large footprints. This means that the dependencies that the `noct`, `database`, and `graphql` plugins require have been moved to optional extras, and are conditionally added to your project during generation based on the configuration flags provided.

If you generate a project without explicitly using an extra, and then try to use its corresponding plugin, your application will fail with a message indicating you're missing the required extra(s). To resolve that issue, edit your API's `pyproject.toml` to include the extra(s) you need:

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
- `testing` for the testing plugin, which adds `pytest`, `pytest-asyncio`, and `requests`. This isn't a generation flag, but provides some useful [pytest](https://docs.pytest.org/en/6.2.x/) utilities and fixtures (such as mock users and tokens for authentication-requiring routes).

### Authenticating with Harbor

Projects generated with `--auth` require Harbor access to download and run the Noct service, Indico's platform-wide authentication server. To setup access:

1. Ensure you have access to a Harbor account (check with your employee contact or DevOps).
2. Login to Harbor through Docker via `docker login -u <username> harbor.devops.indico.io`.

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

## GraphQL

Virga supplies a `GraphQLRoute` that serves as the basic way of exposing Queries and Mutations through a REST endpoint. It accepts a single `Schema` argument, and can be mounted directly to your application via `.add_route`:

```python
app.add_route("/graphql", GraphQLRoute(schema=Schema(query=..., mutation=..., subscription=...)))
```

### Requiring the DB or authentication

The base `GraphQLRoute` provided by Virga does not implement any method for checking authentication or supplying a database connection to downstream resolvers. If your API requires this, use a `SessionedGraphQLRoute` instead.

`SessionedGraphQLRoute` accepts two kwargs: `database_url` and `authenticated`. When `authenticted` is True, the route will check the request's authentication cookies, exactly like `get_current_user`, and if valid will attach `user` and `token` fields to the GQL context. When `database_url` is set, an async db session will be attached to the GQL context via the `db_session` field.

For example:

```python
schema = Schema(query=RootQuery)

# this for no authentication or database access
# it is equivalent to just using GraphQLRoute
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

### Customizing the GraphQL context

In any GraphQL application, you might need to add or control additional things within the GraphQL context. `GraphQLRoute` (and thus `SessionedGraphQLRoute`) allow you to manipulate that context before it is passed to the executor and downstream resolvers.

To do so, just subclass `GraphQLRoute` (or `SessionedGraphQLRoute`) and override the `setup_context` and `cleanup_context` coroutine functions. As the name of them imply, `setup` is run before the context is passed to the Schema and `cleanup` is run afterwards.

```python
async def setup_context(self, context: Dict[str, Any]):
    pass

async def cleanup_context(self, context: Dict[str, Any]):
    pass
```

If you override the functions of an existing subclass, like `SessionedGraphQLRoute`, ensure to call `super()` in both so the lifecycle of other potential objects is handled correctly (like opening and closing a DB connection).
