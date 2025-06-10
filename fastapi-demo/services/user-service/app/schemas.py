from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class User(BaseModel):
    id: int
    name: str
