import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from virga.plugins.database import start_async_session

from .conftest import DB_URL, Widget

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
