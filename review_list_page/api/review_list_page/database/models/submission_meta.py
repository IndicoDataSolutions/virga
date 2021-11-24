import enum
from sqlalchemy import Column, String, Integer, Enum

from .base import BASE


class StatusEnum(enum.Enum):
    unblocked = "UNBLOCKED"
    blocked = "BLOCKED"


class SubmissionMeta(BASE):
    __tablename__ = "submission"
    id = Column(Integer, primary_key=True)
    status = Column(Enum(StatusEnum), default=False)
