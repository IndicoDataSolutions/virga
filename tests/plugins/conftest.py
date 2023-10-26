import asyncio
import os

import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from virga.plugins.database import make_async_engine

# the unit tests themselves serve as tests of the `testing` plugin
from virga.plugins.testing.noct import (  # noqa: F401
    expired_token,
    mock_tokens,
    mock_user,
)

user = os.getenv("POSTGRES_USER")
passwd = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql+asyncpg://{user}:{passwd}@{os.getenv('POSTGRES_HOST')}:5432/{db}"
Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = make_async_engine(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.create)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.drop)
