from pydantic import BaseModel, Field
from typing import Annotated, Literal

class CatSchema(BaseModel):
    name: str
    age: Annotated[int, Field(gt = 0,lt = 100 )]
    weight: Annotated[float, Field(gt=0, lt = 100)]
    breed: Literal['fluffy', 'bold', 'blond', 'degbjuklp']
