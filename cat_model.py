
from typing import Annotated
from sqlmodel import Field, SQLModel


class Cat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: Annotated[int, Field(gt = 0,lt = 100 )]
    weight: Annotated[float, Field(gt=0, lt = 100)]
    breed: str