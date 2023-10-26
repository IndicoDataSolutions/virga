from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from virga.plugins.database import start_async_session

from ..settings import Settings, settings


# https://docs.sqlalchemy.org/en/14/_modules/examples/asyncio/async_orm.html
async def async_session(
    settings: Settings = Depends(settings),
) -> AsyncIterator[AsyncSession]:
    session = start_async_session(settings.db_url)

    try:
        yield session
    finally:
        await session.close()
