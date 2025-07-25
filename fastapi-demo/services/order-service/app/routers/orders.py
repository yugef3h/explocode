import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.clients.product_client import get_product
from app.clients.user_client import get_user
from app.models import ORDER_STATUS_COMPLETED, Order
from app.redis_client import get_redis
from app.schemas import OrderCreate, OrderOut, OrderUpdate
from redis_om import NotFoundError

router = APIRouter(prefix="/orders", tags=["orders"])


async def _complete_order_later(order_pk: str) -> None:
    await asyncio.sleep(2)
    try:
        order = Order.get(order_pk)
    except NotFoundError:
        return
    order.status = ORDER_STATUS_COMPLETED
    order.save()
    fields = {key: str(value) for key, value in order.model_dump().items() if value is not None}
    get_redis().xadd("order_completed", fields)


def _to_out(order: Order) -> OrderOut:
    if order.pk is None:
        raise HTTPException(status_code=500, detail="Order missing primary key")
    return OrderOut(
        id=order.pk,
        user_id=order.user_id,
        product_id=order.product_id,
        item=order.item,
        amount=order.amount,
        quantity=order.quantity,
        status=order.status,
    )


def _get_order(pk: str) -> Order:
    try:
        return Order.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Order not found") from None


@router.get("", response_model=list[OrderOut])
def list_orders() -> list[OrderOut]:
    return [_to_out(Order.get(pk)) for pk in Order.all_pks()]


@router.get("/{pk}", response_model=OrderOut)
def get_order(pk: str) -> OrderOut:
    return _to_out(_get_order(pk))


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreate,
    background_tasks: BackgroundTasks,
) -> OrderOut:
    await get_user(payload.user_id)
    product = await get_product(payload.product_id)

    if product["quantity"] < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient product stock")

    order = Order(
        pk=None,
        user_id=payload.user_id,
        product_id=product["id"],
        item=product["name"],
        amount=product["price"] * payload.quantity,
        quantity=payload.quantity,
    ).save()
    if order.pk is None:
        raise HTTPException(status_code=500, detail="Order missing primary key")
    # 异步任务：2秒后完成订单，先返回 _to_out
    background_tasks.add_task(_complete_order_later, order.pk)
    return _to_out(order)


@router.put("/{pk}", response_model=OrderOut)
async def update_order(pk: str, payload: OrderUpdate) -> OrderOut:
    order = _get_order(pk)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "user_id" in updates:
        await get_user(updates["user_id"])

    for field, value in updates.items():
        setattr(order, field, value)

    return _to_out(order.save())


@router.delete("/{pk}")
def delete_order(pk: str) -> dict[str, str]:
    _get_order(pk)
    Order.delete(pk)
    return {"status": "ok", "message": "Order deleted successfully"}
