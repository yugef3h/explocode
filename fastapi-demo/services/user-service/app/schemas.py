from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    balance: float = Field(default=10000.0, ge=0)


class User(BaseModel):
    id: int
    name: str
    balance: float


class AmountPayload(BaseModel):
    amount: float = Field(gt=0)
