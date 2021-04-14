from pydantic import BaseModel


# Generally, Pydantic models (schemata) only need to be created for data models
# (represented in the models.py file) for REST routes that desire to return raw or
# filtered-attribute objects. For GraphQL applications, there is no need to create
# Pydantic schemata as they are not returned or used for external representation.
#
# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models
class Widget(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
