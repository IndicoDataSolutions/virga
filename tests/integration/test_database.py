import pytest
import os
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, Integer, select
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from virga.plugins.database import make_async_engine, start_async_session

driver = os.getenv("DB_DRIVER", "postgresql+asyncpg")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", 5432)
user = os.getenv("POSTGRES_USER", "")
passwd = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
db = os.getenv("POSTGRES_DB", "")
DB_URL = f"{driver}://{user}:{passwd}@{host}:{port}/{db}"
BASE = declarative_base()


class ExampleUser(BASE):
    __tablename__ = "example_users"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = make_async_engine(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(BASE.metadata.drop_all)
        yield
        await conn.run_sync(BASE.metadata.create_all)


async def async_session():
    session = start_async_session(DB_URL)

    try:
        yield session
    finally:
        session.close()


app = FastAPI()
client = TestClient(app)


async def get_user(session):
    stmt = select(ExampleUser).filter_by(id=1)
    result = await session.execute(stmt)
    return result.one_or_none()


@app.get("/create")
async def create(session: AsyncSession = Depends(async_session)):
    assert not await get_user(session)

    user = ExampleUser(id=1, name="Mickey Mouse")
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
    session.delete(user)
    session.commit()
    assert not await get_user(session)
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
