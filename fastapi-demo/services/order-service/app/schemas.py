from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int = Field(ge=1)
    item: str = Field(min_length=1, max_length=128)
    amount: float = Field(gt=0)


class OrderUpdate(BaseModel):
    user_id: Optional[int] = Field(default=None, ge=1)
    item: Optional[str] = Field(default=None, min_length=1, max_length=128)
    amount: Optional[float] = Field(default=None, gt=0)


class OrderOut(BaseModel):
    id: str
    user_id: int
    item: str
    amount: float
