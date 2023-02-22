from unittest.mock import MagicMock, patch

import aiohttp
from fastapi import FastAPI
from fastapi.testclient import TestClient
from graphene import Mutation, ObjectType, Schema, String
from sqlalchemy import select

from virga.plugins.graphql import SessionedGraphQLRoute
from virga.plugins.noct import VALID_DOMAIN

from .conftest import DB_URL, Widget


class CreateWidget(Mutation):
    class Arguments:
        name = String()

    message = String()

    async def mutate(root, info, name):
        session = info.context["db_session"]
        widget = Widget(name=name)
        session.add(widget)
        await session.commit()
        return CreateWidget(message=f"Widget created with name '{name}'")


class MockQuery(ObjectType):
    get_widget = String(name=String())

    async def resolve_get_widget(self, info, name):
        session = info.context["db_session"]
        stmt = select(Widget).where(Widget.name == name)
        result = await session.execute(stmt)
        widget = result.scalar_one_or_none()

        if widget:
            return f"Widget id for '{name}' is {widget.id}"
        return f"No Widget exists with name '{name}'"


class MockMutation(ObjectType):
    create_widget = CreateWidget.Field()


app = FastAPI()
client = TestClient(app)
schema = Schema(query=MockQuery, mutation=MockMutation)

app.add_route("/database", SessionedGraphQLRoute(schema=schema, database_url=DB_URL))
app.add_route(
    "/authenticated",
    SessionedGraphQLRoute(schema=schema, database_url=DB_URL, authenticated=True),
)


###
###


CREATE_MUTATION = """
    mutation createWidget($name: String) {
        createWidget(name: $name) {
            message
        }
    }
"""
WIDGET_QUERY = """
    query Test($name: String) {
        getWidget(name: $name)
    }
"""


def test_gql_database_noread():
    response = client.post(
        "/database", json={"query": WIDGET_QUERY, "variables": {"name": "Twitter"}}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"getWidget": "No Widget exists with name 'Twitter'"}
    }


def test_gql_database_write():
    # create widget
    response = client.post(
        "/database", json={"query": CREATE_MUTATION, "variables": {"name": "Calendar"}}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"createWidget": {"message": "Widget created with name 'Calendar'"}}
    }

    # read widget
    response = client.post(
        "/database", json={"query": WIDGET_QUERY, "variables": {"name": "Calendar"}}
    )
    assert response.status_code == 200
    assert response.json()["data"]["getWidget"].startswith(
        "Widget id for 'Calendar' is"
    )


def test_gql_auth_invalid():
    response = client.post(
        "/authenticated", json={"query": WIDGET_QUERY, "variables": {"name": "Twitter"}}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Login is required to access this route"}


def test_gql_auth_write(mock_tokens):
    auth_token, _, _, _ = mock_tokens

    response = client.post(
        "/authenticated",
        json={"query": CREATE_MUTATION, "variables": {"name": "AuthCalendar"}},
        cookies={"auth_token": auth_token},
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"createWidget": {"message": "Widget created with name 'AuthCalendar'"}}
    }

    response = client.post(
        "/authenticated",
        json={"query": WIDGET_QUERY, "variables": {"name": "AuthCalendar"}},
        cookies={"auth_token": auth_token},
    )
    assert response.status_code == 200
    assert response.json()["data"]["getWidget"].startswith(
        "Widget id for 'AuthCalendar' is"
    )


def test_gql_auth_refresh(monkeypatch, expired_token, mock_tokens, event_loop):
    _, refresh_token, _, _ = mock_tokens

    # patch aiosession for magic mocks
    aiosession = aiohttp.ClientSession(
        headers={"Host": f"virga.{VALID_DOMAIN}"}, loop=event_loop
    )
    aiosession.post = MagicMock(side_effect=aiosession.post)
    aiosession.close = MagicMock(side_effect=aiosession.close)

    with patch(
        "virga.plugins.noct.handler.aiohttp.ClientSession",
        return_value=aiosession,
    ) as mock:
        # context manager runs app startup/shutdown
        with client:
            for _ in range(2):
                response = client.post(
                    "/authenticated",
                    json={"query": WIDGET_QUERY, "variables": {"name": "Twitter"}},
                    cookies={
                        "auth_token": expired_token,
                        "refresh_token": refresh_token,
                    },
                )
                assert response.status_code == 200
                assert response.json() == {
                    "data": {"getWidget": "No Widget exists with name 'Twitter'"}
                }

        # ensure aiosession is created once
        mock.assert_called_once()
        # but that post is called twice
        assert aiosession.post.call_count == 2
        # and that the session is cleaned up by the shutdown lifecycle
        aiosession.close.assert_called_once()
