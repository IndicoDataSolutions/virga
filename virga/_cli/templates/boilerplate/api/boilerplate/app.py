from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import Settings, settings

# from virga.plugins.noct import User, get_current_user

# from graphene import Schema
# from virga.plugins.graphql import SessionedGraphQLRoute
# from .gql import RootQuery

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from .database import async_session
# from .database.models import Widget


app = FastAPI(root_path="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Origin",
        "Authorization",
        "X-Requested-With",
        "x-xsrftoken",
    ],
)


@app.get("/ping")
def pong() -> bool:
    """
    Returns HTTP 200 OK when the application is live and ready to receive requests. This
    can be used as a healthcheck endpoint in deployment configurations.
    """
    return True


@app.get("/")
async def home(settings: Settings = Depends(settings)) -> Dict[str, str]:
    return {settings.app_name: "Hello World!"}


# # Makes use of Noct middleware to fetch the current authenticated user.
# @app.get("/user")
# async def user_home(current_user: User = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user.email}!"}


# # Spawn an asynchronous database session and fetch a database object.
# # https://docs.sqlalchemy.org/en/14/orm/session_basics.html
# # https://docs.sqlalchemy.org/en/14/orm/session_basics.html#querying-2-0-style
# @app.get("/db")
# async def db_home(session: AsyncSession = Depends(async_session)):
#     stmt = select(Widget).where(Widget.id == 1)
#     result = await session.execute(stmt)
#     result = result.scalar_one()
#     return {"message": f"This is a {result.name} widget!"}


# # Mounts a Graphene executor with schema to a route. POST requests to
# # the route get executed while GET requests will render GraphiQL. GraphQLRoute
# # accepts any Graphene Schema object.
# #
# # SessionedGraphQLRoute (recommended) also accepts two kwargs, `database_url` and
# # `authenticated`:
# #
# # - When `authenticted` is True, the route will check the request authentication
# #   cookies, exactly like `get_current_user`, and if valid will attach `user` and
# #   `token` fields to the GQL context passed to resolvers.
# #
# # - When set, `database_url` will be used to start an async db session. The session
# #   will be attached to the GQL context via the `db` field.
# #
# #
# # Read more:
# # https://docs.graphene-python.org/en/stable/types/schema/
# # https://graphql.org/learn/execution/#root-fields-resolvers
# schema = Schema(query=RootQuery)
# app.add_route("/graphql", SessionedGraphQLRoute(schema=schema))
# app.add_route("/gql_auth", SessionedGraphQLRoute(schema=schema, authenticated=True))
# app.add_route(
#     "/gql_db", SessionedGraphQLRoute(schema=schema, database_url=settings().db_url)
# )
