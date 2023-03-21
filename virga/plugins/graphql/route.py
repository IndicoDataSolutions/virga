import asyncio
import pathlib
from typing import Any, Callable, Dict, Union

from fastapi import BackgroundTasks, Response, status
from fastapi.responses import FileResponse, ORJSONResponse, PlainTextResponse
from starlette.requests import Request
from starlette.types import Receive, Scope, Send

# complain if graphql extra isn't installed
try:
    import graphene
    from graphql import format_error
    from graphql.execution.executors.asyncio import AsyncioExecutor
except ImportError:
    graphene = None  # type: ignore


GRAPHIQL = str(pathlib.Path(__file__).parent / "graphiql.html")


class GraphQLRoute:
    def __init__(
        self, schema: Union["graphene.Schema", Callable[[Request], "graphene.Schema"]]
    ):
        assert (
            graphene is not None
        ), "virga[graphql] extra must be installed to use the GraphQL plugin"

        self.schema = schema

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive=receive)
        response = await self._handle_request(request)
        await response(scope, receive, send)

    async def _handle_request(self, request: Request) -> Response:
        # route GET requests to the IDE
        if request.method == "GET" and "text/html" in request.headers.get("Accept", ""):
            # read the GraphiQL playground html and serve it as content
            return FileResponse(GRAPHIQL, media_type="text/html")
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
        self._build_context_cache(context)
        await self.setup_context(context)

        # execute the graphql query on the assigned schema
        # if schema is callable, call it to fetch the schema
        schema = self.schema(request) if callable(self.schema) else self.schema
        executor = AsyncioExecutor(loop=asyncio.get_event_loop())
        result = await schema.execute(
            query,
            variable_values=variables,
            context_value=context,
            executor=executor,
            return_promise=True,
        )

        await self.cleanup_context(context)

        # parse graphql result
        response = {}
        if not result.invalid:
            response["data"] = result.data
        if result.errors:
            response["errors"] = [format_error(e) for e in result.errors]

        return ORJSONResponse(
            response, status_code=status.HTTP_200_OK, background=background
        )

    def _build_context_cache(self, context):
        # Allow loader and request caching through the request context and get_* methods
        loaders: Dict[Callable, Any] = {}
        clients: Dict[Callable, Any] = {}

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

        context["get_loader"] = get_loaders
        context["get_client"] = get_clients

    async def setup_context(self, context: Dict[str, Any]):
        """
        Allows customization of the GraphQL context. This gets run before the executor
        resolves the GraphQL request.
        """
        pass

    async def cleanup_context(self, context: Dict[str, Any]):
        """
        Allows cleanup of any objects stored within the GraphQL context. This gets run
        after the executor resolves the GraphQL request and generates a response.
        """
        pass
