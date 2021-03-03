from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from graphene import ObjectType, String, Schema

from virga.plugins.graphql import GraphQLRoute

app = FastAPI()
client = TestClient(app)


class MockLoaderClient:
    def __init__(self, name):
        self.name = name + " :("


class MockQuery(ObjectType):
    hello = String(name=String(default_value="Stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name


class MockLoaderClientQuery(ObjectType):
    goodbye = String(name=String(default_value="Stranger"))

    def resolve_goodbye(self, info, name):
        client = info.context.get("get_client")(MockLoaderClient, name)
        client2 = info.context.get("get_client")(MockLoaderClient, "banana")
        assert client is client2

        return "Goodbye " + client.name


class Query(MockQuery, MockLoaderClientQuery):
    pass


def get_schema(request: Request):
    return Schema(query=Query)


app.add_route("/static", GraphQLRoute(schema=Schema(query=Query)))
app.add_route("/dynamic", GraphQLRoute(schema=get_schema))


###
###


HELLO_QUERY = """
    query Test($name: String) {
        hello(name: $name)
    }
"""
GOODBYE_QUERY = """
    query Test($name: String) {
        goodbye(name: $name)
    }
"""


def test_graphiql():
    response = client.get("/static", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert response.text.find("<title>GraphiQL</title>") > -1


def test_graphql_bad_media_type():
    response = client.post(
        "/static", data={"query": HELLO_QUERY, "variables": {"name": "World"}},
    )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


def test_graphql_bad_method():
    response = client.put(
        "/static", data={"query": HELLO_QUERY, "variables": {"name": "World"}},
    )
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


def test_graphql_bad_request():
    response = client.post("/static", json={"variables": {"name": "World"}},)
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


def test_graphql_static():
    response = client.post(
        "/static", json={"query": HELLO_QUERY, "variables": {"name": "Dave"}},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello Dave"}}


def test_graphql_static_clients_loaders():
    response = client.post(
        "/static", json={"query": GOODBYE_QUERY, "variables": {"name": "World"}},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"goodbye": "Goodbye World :("}}


def test_graphql_dynamic():
    response = client.post(
        "/dynamic", json={"query": HELLO_QUERY, "variables": {"name": "Dave"}},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello Dave"}}