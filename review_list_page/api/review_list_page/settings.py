import os

from pydantic import BaseSettings
from typing import Tuple

from functools import lru_cache


# Objects and arguments passed through dependency injection must be hashable.
# Passing `frozen=True` to pydantic models ensures hashability at the
# expense of mutability (which is not required for environment-based settings).
#
# Read more:
#   - https://github.com/tiangolo/fastapi/issues/1985
#   - https://github.com/samuelcolvin/pydantic/pull/1881
class Settings(BaseSettings, frozen=True):
    app_name: str = "review_list_page"
    db_driver: str = "postgresql+asyncpg"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str
    indico_host: str = "app.indico.io"
    indico_api_token: str = os.getenv("INDICO_API_TOKEN")
    workflow_ids: Tuple[int] = (1435,)

    @property
    @lru_cache(maxsize=None)
    def db_url(self):
        # dialect+driver://username:password@host:port/database
        return "{}://{}:{}@{}:{}/{}".format(
            self.db_driver,
            self.postgres_user,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_db,
        )


@lru_cache(maxsize=None)
def settings():
    return Settings()
