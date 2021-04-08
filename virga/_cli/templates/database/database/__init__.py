from sqlalchemy.ext.declarative import declarative_base
from virga.plugins.database import start_async_session

from ..settings import get_settings

BASE = declarative_base()


# https://docs.sqlalchemy.org/en/14/_modules/examples/asyncio/async_orm.html
def async_session():
    settings = get_settings()
    session = start_async_session(settings.db_url)

    try:
        yield session
    finally:
        session.close()
