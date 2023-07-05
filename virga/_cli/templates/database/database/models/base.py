from typing import Type

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

BASE: Type[DeclarativeMeta] = declarative_base()
