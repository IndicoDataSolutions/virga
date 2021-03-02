from functools import lru_cache

from fastapi import FastAPI, Depends
from .settings import Settings


app = FastAPI()


@lru_cache()
def get_settings():
    return Settings()


@app.get("/")
async def read_root(settings: Settings = Depends(get_settings)):
    return {settings.app_name: "Hello World!"}
