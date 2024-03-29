from graphene import ObjectType, String, ResolveInfo


#
# Queries are constructed following the conventions and examples provided
# under the Graphene documentation.
#
# https://docs.graphene-python.org/en/stable/execution/execute/
#
class ExampleQueryHello(ObjectType):  # type: ignore
    hello = String(name=String(default_value="Dave"))

    @staticmethod
    def resolve_hello(parent: None, info: ResolveInfo, name: str) -> str:
        return f"Hello {name}!"


#
# Mutations are similar to Queries when exposing via an API, but differ
# conceptually when it comes to operating with data.
#
# https://docs.graphene-python.org/en/stable/types/mutations/
#


#
# DataLoaders can be used to fetch data from external sources, or simply
# operate on data that need more complex processing.
#
# https://docs.graphene-python.org/en/stable/execution/dataloader/
#
# As opposed to creating globals instances for DataLoaders, Virga enables
# instantiating loaders from within Query or Mutation resolvers, which
# may then be cached and persisted for the duration of the executation
# chain (all downstream resolvers will have access to it).
class ExampleDataLoader:
    def __init__(self, appendage: str):
        self.appendage = appendage

    def append_to(self, name: str) -> str:
        return f"{name} {self.appendage}"


class ExampleQueryGoodbye(ObjectType):  # type: ignore
    goodbye = String(name=String(default_value="Stranger"))

    @staticmethod
    def resolve_goodbye(parent: None, info: ResolveInfo, name: str) -> str:
        # an instance of ExampleDataLoader does not exist in the context,
        # so a new one will be created and cached. Calling `get_loader`
        # will yield the same literal instance.
        loader = info.context["get_loader"](ExampleDataLoader, ":(")
        return f"Goodbye, {loader.append_to(name)}"


#
# To combine multiple queries or mutations, simple Python multi-inheritance
# will work. Note that GraphQL is data-centric, so different queries/mutations
# sharing the same name is nonsensical and not supported --(Data representing
# different things/operations should not share the same name).
class RootQuery(ExampleQueryHello, ExampleQueryGoodbye):
    pass
