from fastapi import Depends

from virga.plugins.database import start_async_session

from ..settings import Settings, settings


# https://docs.sqlalchemy.org/en/14/_modules/examples/asyncio/async_orm.html
async def async_session(settings: Settings = Depends(settings)):
    session = start_async_session(settings.db_url)

    try:
        yield session
    finally:
        session.close()
