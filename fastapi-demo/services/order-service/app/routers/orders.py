from fastapi import APIRouter, HTTPException

from app.clients.user_client import get_user
from app.schemas import Order, OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])

_orders: dict[int, Order] = {}
_next_id = 1


@router.get("", response_model=list[Order])
def list_orders() -> list[Order]:
    return list(_orders.values())


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int) -> Order:
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=Order, status_code=201)
async def create_order(payload: OrderCreate) -> Order:
    global _next_id

    await get_user(payload.user_id)

    order = Order(
        id=_next_id,
        user_id=payload.user_id,
        item=payload.item,
        amount=payload.amount,
    )
    _orders[_next_id] = order
    _next_id += 1
    return order
