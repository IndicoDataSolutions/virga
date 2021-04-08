from fastapi import FastAPI, Depends

# from virga.types import User
# from virga.plugins.noct import get_current_user

# from graphene import Schema
# from virga.plugins.graphql import GraphQLRoute
# from .gql import RootQuery

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from .database import async_session
# from .database.models import ExampleUser

from .settings import Settings, settings

app = FastAPI()


@app.get("/")
async def home(settings: Settings = Depends(settings)):
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
#     stmt = select(ExampleUser).filter_by(id=1)
#     result = await session.execute(stmt)
#     result = result.scalars().first()
#     return {"message": f"Hello, {result.name}!"}


# # Mounts a Graphene executor with schema to '/graphql'. POST requests to
# # the route get executed while GET requests will render GraphiQL.
# # GraphQLRoute accepts any Graphene Schema object.
# #
# # Read more: https://docs.graphene-python.org/en/stable/types/schema/
# app.add_route("/graphql", GraphQLRoute(schema=Schema(query=RootQuery)))
