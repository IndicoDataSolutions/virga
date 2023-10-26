from typing import TypedDict

NoctCookie = TypedDict(
    "NoctCookie",
    {
        "key": str,
        "value": str,
        "domain": str,
        "httponly": bool,
        "secure": bool,
    },
)
