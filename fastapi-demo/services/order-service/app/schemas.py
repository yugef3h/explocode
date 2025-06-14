from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int = Field(ge=1)
    item: str = Field(min_length=1, max_length=128)
    amount: float = Field(gt=0)


class Order(BaseModel):
    id: int
    user_id: int
    item: str
    amount: float
