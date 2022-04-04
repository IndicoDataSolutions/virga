from sqlalchemy import Column, Integer, String

from .base import BASE


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-database-models
class Widget(BASE):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
