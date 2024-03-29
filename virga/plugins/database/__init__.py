from typing import Any, Optional

import orjson

# complain if database extra isn't installed
try:
    import sqlalchemy
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
except ImportError:
    sqlalchemy = None  # type: ignore


def make_async_engine(url: str, **kwargs: Any) -> "AsyncEngine":
    """
    Create and return an asyncio database engine from the DB_INFO environment variable.
    """
    assert (
        sqlalchemy is not None
    ), "virga[database] extra must be installed to use the database plugin"

    # pool parameters
    kwargs["pool_recycle"] = kwargs.get("pool_recycle", 200)
    kwargs["pool_timeout"] = kwargs.get("pool_timeout", 30)
    kwargs["pool_size"] = kwargs.get("pool_size", 5)
    kwargs["max_overflow"] = kwargs.get("max_overflow", 10)
    kwargs["pool_reset_on_return"] = "rollback"
    kwargs["pool_pre_ping"] = True

    # use orjson for faster json (de)serializing
    kwargs["json_serializer"] = orjson.dumps
    kwargs["json_deserializer"] = orjson.loads

    kwargs["execution_options"] = kwargs.get(
        "execution_options", {"schema_translate_map": {None: "public"}}
    )

    kwargs["future"] = True
    kwargs["echo"] = kwargs.get("echo", True)

    return create_async_engine(url, **kwargs)


class _SessionMaker:
    _sessionmaker: Optional["sessionmaker[AsyncSession]"] = None
    _engine: Optional["AsyncEngine"] = None

    @classmethod
    def new(cls, db_url: str, **kwargs: Any) -> "AsyncSession":
        if not cls._sessionmaker:
            cls._engine = make_async_engine(db_url, **kwargs)
            cls._sessionmaker = sessionmaker(
                bind=cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                future=True,
            )

        session: AsyncSession = cls._sessionmaker()
        return session


def start_async_session(db_url: str, **kwargs: Any) -> "AsyncSession":
    """
    Create and return a new asyncio-backed database session. The underlying
    sqlalchemy sessionmaker and engine are created once and cached.
    """
    return _SessionMaker.new(db_url, **kwargs)
