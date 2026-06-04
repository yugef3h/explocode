from pydantic import BaseModel, Field


class HelloResponse(BaseModel):
    message: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class QuantityPayload(BaseModel):
    quantity: int = Field(ge=1)
