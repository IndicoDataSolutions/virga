from unittest.mock import MagicMock

import pytest
from virga.plugins.database import make_async_engine
from virga.plugins.graphql import GraphQLRoute, SessionedGraphQLRoute
from virga.plugins.noct import read_user


async def test_missing_database(monkeypatch):
    monkeypatch.setattr("virga.plugins.database.sqlalchemy", None)
    monkeypatch.setattr("virga.plugins.database._SessionMaker._sessionmaker", None)

    with pytest.raises(AssertionError, match="database"):
        make_async_engine(None)

    with pytest.raises(AssertionError, match="database"):
        await SessionedGraphQLRoute(schema=None, database_url="mock")._execute_graphql(
            None, None, None
        )


def test_missing_graphql(monkeypatch):
    monkeypatch.setattr("virga.plugins.graphql.route.graphene", None)

    with pytest.raises(AssertionError, match="graphql"):
        GraphQLRoute(schema=None)

    with pytest.raises(AssertionError, match="graphql"):
        SessionedGraphQLRoute(schema=None)


async def test_missing_read_user(monkeypatch):
    monkeypatch.setattr("virga.plugins.noct.handler.aiohttp", None)

    with pytest.raises(AssertionError, match="auth"):
        await read_user(None)

    with pytest.raises(AssertionError, match="auth"):
        await SessionedGraphQLRoute(schema=None, authenticated=True)._handle_request(
            MagicMock()
        )
