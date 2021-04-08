from sqlalchemy.ext.declarative import declarative_base
from virga.plugins.database import start_async_session
from fastapi import Depends

from ..settings import Settings, settings

BASE = declarative_base()


# https://docs.sqlalchemy.org/en/14/_modules/examples/asyncio/async_orm.html
async def async_session(settings: Settings = Depends(settings)):
    session = start_async_session(settings.db_url)

    try:
        yield session
    finally:
        session.close()
