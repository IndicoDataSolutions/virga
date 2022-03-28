from fastapi import Request, Response

from virga.plugins.database import start_async_session
from virga.plugins.noct.noct import (
    ExpiredTokenException,
    LoginRequiredException,
    _get_current_user,
    _refresh_token,
    write_secure_cookie,
)

from .graphql import GraphQLRoute


class SessionedGraphQLRoute(GraphQLRoute):
    def __init__(self, schema, authenticated=False, database_url=None):
        super().__init__(schema=schema)
        self.check_auth = authenticated
        self.database_url = database_url

    async def _handle_request(self, request: Request) -> Response:
        # if the route should check authentication
        if self.check_auth:
            auth_token = request.cookies.get("auth_token")
            refresh_token = request.cookies.get("refresh_token")

            if not auth_token and not refresh_token:
                raise LoginRequiredException()

            # decode or refresh token if necessary
            try:
                self.user = _get_current_user(cookie=auth_token)
                self.token = auth_token
                self.domain = None
            except ExpiredTokenException:
                self.token, self.domain = _refresh_token(refresh_token)
                self.user = _get_current_user(token=self.token)

        # handle graphql request as per normal
        response = await super()._handle_request(request)

        if self.check_auth and self.domain:
            # set cookie if dirty
            response.set_cookie(
                "auth_token",
                write_secure_cookie("auth_token", self.token),
                domain=self.domain,
                httponly=True,
                secure=True,
            )

        return response

    async def _execute_graphql(self, query, variables, context):
        # if authentication, set context user and token
        if self.check_auth:
            context["user"] = self.user
            context["token"] = self.token

        # if a database connection should be available to resolvers
        if self.database_url:
            context["db_session"] = start_async_session(self.database_url)

        result = await super()._execute_graphql(query, variables, context)

        if self.database_url:
            # ensure the db session is closed after graphql execution
            await context["db_session"].close()

        return result
