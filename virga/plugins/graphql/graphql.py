import asyncio
from typing import Union, Callable, Any
import pathlib

import graphene
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql import format_error

from starlette.types import Receive, Scope, Send
from starlette.requests import Request
from fastapi import (
    Request,
    Response,
    status,
    BackgroundTasks,
)
from fastapi.responses import HTMLResponse, ORJSONResponse, PlainTextResponse


class GraphQLRoute:
    def __init__(
        self, schema: Union[graphene.Schema, Callable[[Request], graphene.Schema]]
    ):
        self.schema = schema

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive=receive)
        response = await self._handle_request(request)
        await response(scope, receive, send)

    async def _handle_request(self, request: Request) -> Response:
        # route GET requests to the IDE
        if request.method == "GET" and "text/html" in request.headers.get("Accept", ""):
            # read the GraphiQL playground html and serve it as content
            graphiql = pathlib.Path(__file__).parent / "graphiql.html"
            raw_html = None

            with open(graphiql.absolute(), "r") as f:
                raw_html = f.read()

            return HTMLResponse(raw_html)
        # route POST requests to the graphql executor
        elif request.method == "POST":
            content_type = request.headers.get("Content-Type", "")

            # parse graphql according to content type
            if "application/json" in content_type:
                data = await request.json()
            else:
                return PlainTextResponse(
                    "Unsupported Media Type",
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                )
        else:
            return PlainTextResponse(
                "Method Not Allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        # attempt to pull final query and vars
        try:
            query = data["query"]
            variables = data.get("variables")
        except KeyError:
            return PlainTextResponse(
                "No GraphQL query found in the request",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # construct foundation fastapi context
        background = BackgroundTasks()
        context = {"request": request, "background": background}
        result = await self._execute_graphql(query, variables, context)

        # parse graphql result
        response = {}
        if not result.invalid:
            response["data"] = result.data
        if result.errors:
            response["errors"] = [format_error(e) for e in result.errors]

        status_code = (
            status.HTTP_400_BAD_REQUEST if result.errors else status.HTTP_200_OK
        )

        return ORJSONResponse(response, status_code=status_code, background=background)

    async def _execute_graphql(self, query, variables, context):
        # execute the graphql query on the assigned schema
        # if schema is callable, call it to fetch the schema
        schema = (
            self.schema(context["request"]) if callable(self.schema) else self.schema
        )

        context.update(self._build_context_cache())
        executor = AsyncioExecutor(loop=asyncio.get_event_loop())

        result = await schema.execute(
            query,
            variable_values=variables,
            context_value=context,
            executor=executor,
            return_promise=True,
        )

        return result

    def _build_context_cache(self):
        # Allow loader and request caching through the request context and get_* methods
        loaders = {}
        clients = {}

        def get_loaders(loader_type, *args: Any, **kwargs: Any):
            loader = loaders.get(loader_type)

            if not loader:
                loader = loader_type(*args, **kwargs)
                loaders[loader_type] = loader

            return loader

        def get_clients(client_type, *args: Any, **kwargs: Any):
            client = clients.get(client_type)

            if not client:
                client = client_type(*args, **kwargs)
                clients[client_type] = client

            return client

        context = {
            "get_loader": get_loaders,
            "get_client": get_clients,
        }
        return context