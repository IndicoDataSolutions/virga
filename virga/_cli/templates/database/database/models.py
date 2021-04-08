from sqlalchemy import Column, String, Integer

from . import BASE


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-database-models
class ExampleUser(BASE):
    __tablename__ = "example_users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
