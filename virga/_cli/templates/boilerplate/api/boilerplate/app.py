from functools import lru_cache
from fastapi import FastAPI, Depends

# from virga.types import User
# from virga.plugins.noct import get_current_user

# from graphene import Schema
# from virga.plugins.graphql import GraphQLRoute
# from .gql import RootQuery

from .settings import Settings

app = FastAPI()


@lru_cache()
def get_settings():
    return Settings()


# # Makes use of Noct middleware to fetch the current authenticated user.
# @app.get("/user_info")
# async def get_user(current_user: User = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user.email}!"}


@app.get("/")
async def read_root(settings: Settings = Depends(get_settings)):
    return {settings.app_name: "Hello World!"}


# # Mounts a Graphene executor with schema to '/graphql'. POST requests to
# # the route get executed while GET requests will render GraphiQL.
# # GraphQLRoute accepts any Graphene Schema object.
# #
# # Read more: https://docs.graphene-python.org/en/stable/types/schema/
# app.add_route("/graphql", GraphQLRoute(schema=Schema(query=RootQuery)))