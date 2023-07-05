import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

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
