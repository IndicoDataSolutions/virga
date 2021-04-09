import pytest
import os
import asyncio
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, Integer, select
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from virga.plugins.database import make_async_engine, start_async_session

user = os.getenv("POSTGRES_USER")
passwd = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql+asyncpg://{user}:{passwd}@virga-db:5432/{db}"
BASE = declarative_base()


class ExampleUser(BASE):
    __tablename__ = "example_users"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = make_async_engine(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(BASE.metadata.reflect)
        await conn.run_sync(BASE.metadata.drop_all)
        await conn.run_sync(BASE.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(BASE.metadata.reflect)
        await conn.run_sync(BASE.metadata.drop_all)


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


async def get_user(session):
    stmt = select(ExampleUser).where(ExampleUser.id == 1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


@app.get("/create")
async def create(session: AsyncSession = Depends(async_session)):
    assert not await get_user(session)

    user = ExampleUser(name="Mickey Mouse")
    session.add(user)
    await session.commit()

    user = await get_user(session)
    assert user
    return {"message": f"Welcome, {user.name}!"}


@app.get("/read")
async def read(session: AsyncSession = Depends(async_session)):
    user = await get_user(session)
    assert user
    return {"message": f"Hello, {user.name}!"}


@app.get("/delete")
async def delete(session: AsyncSession = Depends(async_session)):
    user = await get_user(session)
    await session.delete(user)
    await session.commit()

    assert not await get_user(session)
    assert user not in session
    return {"message": f"Goodbye, {user.name}!"}


###
###


@pytest.mark.parametrize(
    "query,message", [("create", "Welcome"), ("read", "Hello"), ("delete", "Goodbye")]
)
def test_db(query, message):
    response = client.get(f"/{query}")
    assert response.status_code == 200
    assert response.json() == {"message": f"{message}, Mickey Mouse!"}
