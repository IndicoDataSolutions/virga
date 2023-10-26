from typing import Optional, List, Any

from pydantic import BaseModel


# this model should mimic atmosphere
# https://git.io/Jtj8E
class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    scopes: Optional[List[str]] = None

    def __init__(self, **data: Any):
        """Parse the noct payload into user properties."""
        fields = {}

        for k, v in data.items():
            if k.startswith("user_"):
                fields[k.replace("user_", "", 1)] = v
            elif k == "aud":
                fields["scopes"] = v

        super().__init__(**fields)
