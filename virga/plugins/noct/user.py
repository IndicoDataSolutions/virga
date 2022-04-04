from typing import Optional

from pydantic import BaseModel


# this model should mimic atmosphere
# https://git.io/Jtj8E
class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    scopes: Optional[list] = None

    def __init__(self, **data):
        fields = {}

        for k, v in data.items():
            if k.startswith("user_"):
                fields[k.replace("user_", "", 1)] = v
            elif k == "aud":
                fields["scopes"] = v

        super().__init__(**fields)
