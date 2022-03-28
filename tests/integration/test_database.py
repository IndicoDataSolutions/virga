import asyncio
import os

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from virga.plugins.database import make_async_engine, start_async_session

user = os.getenv("POSTGRES_USER")
passwd = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql+asyncpg://{user}:{passwd}@test-db:5432/{db}"
Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture(scope="session", autouse=True)
async def prepare_dataBase():
    engine = make_async_engine(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.create)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.drop)


# https://stackoverflow.com/a/56238383
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


app = FastAPI()
client = TestClient(app)


async def async_session():
    session = start_async_session(DB_URL)

    try:
        yield session
    finally:
        await session.close()


async def get_widget(session):
    stmt = select(Widget).where(Widget.id == 1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


@app.get("/create")
async def create(session: AsyncSession = Depends(async_session)):
    assert not await get_widget(session)

    widget = Widget(name="Calendar")
    session.add(widget)
    await session.commit()

    widget = await get_widget(session)
    assert widget
    return {"message": f"Created the {widget.name} widget!"}


@app.get("/read")
async def read(session: AsyncSession = Depends(async_session)):
    widget = await get_widget(session)
    assert widget
    return {"message": f"Fetching the {widget.name} widget!"}


@app.get("/delete")
async def delete(session: AsyncSession = Depends(async_session)):
    widget = await get_widget(session)
    await session.delete(widget)
    await session.commit()

    assert not await get_widget(session)
    assert widget not in session
    return {"message": f"Removing the {widget.name} widget!"}


###
###


@pytest.mark.parametrize(
    "query,message",
    [("create", "Created"), ("read", "Fetching"), ("delete", "Removing")],
)
def test_db(query, message):
    response = client.get(f"/{query}")
    assert response.status_code == 200
    assert response.json() == {"message": f"{message} the Calendar widget!"}
