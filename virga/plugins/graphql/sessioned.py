from typing import Any, Dict, Optional

from fastapi import Request, Response

from virga.plugins.database import start_async_session
from virga.plugins.noct import LoginRequiredException, read_user

from .route import GraphQLRoute, graphene  # type: ignore[attr-defined]


class SessionedGraphQLRoute(GraphQLRoute):
    def __init__(
        self,
        schema: "graphene.Schema",
        authenticated: bool = False,
        database_url: Optional[str] = None,
    ):
        super().__init__(schema=schema)
        self.check_auth: bool = authenticated
        self.database_url: Optional[str] = database_url

    async def _handle_request(self, request: Request) -> Response:
        # if the route should check authentication
        if self.check_auth:
            auth_token = request.cookies.get("auth_token")
            refresh_token = request.cookies.get("refresh_token")

            if not auth_token and not refresh_token:
                raise LoginRequiredException()

            # decode or refresh token if necessary
            self.user, self.token, self.cookie = await read_user(
                request, auth_token=auth_token, refresh_token=refresh_token
            )

        # handle graphql request as per normal
        response: Response = await super()._handle_request(request)

        if self.check_auth and self.cookie:
            # set cookie if dirty
            response.set_cookie(
                self.cookie["key"],
                value=self.cookie["value"],
                domain=self.cookie["domain"],
                secure=self.cookie["secure"],
                httponly=self.cookie["httponly"],
            )

        return response

    async def setup_context(self, context: Dict[str, Any]) -> None:
        # if authentication, set context user and token
        if self.check_auth:
            context["user"] = self.user
            context["token"] = self.token

        # if a database connection should be available to resolvers
        if self.database_url:
            context["db_session"] = start_async_session(self.database_url)

    async def cleanup_context(self, context: Dict[str, Any]) -> None:
        if self.database_url:
            # ensure the db session is closed after graphql execution
            await context["db_session"].close()
