from graphene import ObjectType, String


class ExampleQueryHello(ObjectType):
    hello = String(name=String(default_value="Dave"))

    def resolve_hello(self, info, name):
        return f"Hello {name}!"


class ExampleQueryGoodbye(ObjectType):
    goodbye = String(name=String(default_value="Stranger"))

    def resolve_goodbye(self, info, name):
        return f"Goodbye, {name}."


class RootQuery(ExampleQueryHello, ExampleQueryGoodbye):
    pass
