import orjson
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


def make_async_engine(config: dict, **kwargs) -> AsyncEngine:
    """
    Create and return an asyncio database engine from the DB_INFO environment variable.
    """
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

    return create_async_engine(URL(**config), **kwargs)


class _SessionMaker(object):
    _sessionmaker = None
    _engine = None

    @classmethod
    def new(cls, db_config, **kwargs):
        if not cls._sessionmaker or not cls._engine:
            cls._engine = make_async_engine(db_config, **kwargs)
            cls._sessionmaker = sessionmaker(
                cls._engine, expire_on_commit=False, class_=AsyncSession
            )

        return cls._sessionmaker()


def start_async_session(db_config: dict, **kwargs) -> AsyncSession:
    """
    Create and return a new asyncio-backed database session. The underlying
    sqlalchemy sessionmaker and engine are created once anc cached.
    """
    return _SessionMaker.new(db_config, **kwargs)
