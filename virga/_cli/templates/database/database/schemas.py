from pydantic import BaseModel


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models
class ExampleUser(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
