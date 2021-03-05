from functools import lru_cache
from fastapi import FastAPI, Depends

# from virga.types import User
# from virga.requests.noct import get_current_user

from .settings import Settings

app = FastAPI()


@lru_cache()
def get_settings():
    return Settings()


# # Makes use of Noct middleware to fetch the current authenticated user
# @app.get("/user_info")
# async def get_user(current_user: User = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user.name}!"}


@app.get("/")
async def read_root(settings: Settings = Depends(get_settings)):
    return {settings.app_name: "Hello World!"}
