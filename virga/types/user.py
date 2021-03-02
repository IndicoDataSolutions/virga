from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    email: str

    def __init__(self, **data):
        fields = {}

        for k, v in data.items():
            if k.startswith("user_"):
                fields[k.replace("user_", "", 1)] = v

        super().__init__(**fields)
