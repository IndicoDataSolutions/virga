from fastapi import Request, Response
from virga.plugins.database import start_async_session
from virga.plugins.noct import LoginRequiredException, read_user

from .route import GraphQLRoute


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
            self.user, self.token, self.cookie = await read_user(
                request, auth_token=auth_token, refresh_token=refresh_token
            )

        # handle graphql request as per normal
        response = await super()._handle_request(request)

        if self.check_auth and self.cookie:
            # set cookie if dirty
            response.set_cookie(**self.cookie)

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
