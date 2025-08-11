import logging
import time
from threading import Event

import httpx
from redis.exceptions import ResponseError
from redis_om import NotFoundError

from app.config import settings
from app.consumer_state import ConsumerState
from app.idempotency import confirm, is_done, release_claim, try_claim
from app.models import ORDER_STATUS_REFUNDED, Order
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

STREAM_KEY = "inventory_failed"
GROUP_NAME = "order-service"
CONSUMER_NAME = "refund-worker"
REFUND_KEY_PREFIX = "order_refunded:"


def _decode(value):
    return value.decode() if isinstance(value, bytes) else value


def _ensure_consumer_group(redis) -> None:
    try:
        redis.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def _refund_user(user_id: int, amount: float) -> None:
    url = f"{settings.user_service_url.rstrip('/')}/users/{user_id}/refund"
    with httpx.Client(timeout=5.0, trust_env=False) as client:
        response = client.post(url, json={"amount": amount})
    if response.status_code >= 400:
        raise RuntimeError(
            f"refund failed for user {user_id}: HTTP {response.status_code}"
        )


def _release_stock(product_id: str, quantity: int) -> None:
    url = f"{settings.a_service_url.rstrip('/')}/products/{product_id}/release"
    with httpx.Client(timeout=5.0, trust_env=False) as client:
        response = client.post(url, json={"quantity": quantity})
    if response.status_code >= 400:
        raise RuntimeError(
            f"release stock failed for product {product_id}: HTTP {response.status_code}"
        )


def _handle_message(fields: dict, redis) -> bool:
    decoded = {_decode(k): _decode(v) for k, v in fields.items()}
    order_id = decoded.get("order_id")
    user_id = decoded.get("user_id")
    amount_raw = decoded.get("amount")
    product_id = decoded.get("product_id")
    quantity_raw = decoded.get("quantity")
    reason = decoded.get("reason", "unknown")

    if not order_id or not user_id or not amount_raw:
        logger.warning("skip invalid inventory_failed message: %s", decoded)
        return True

    idempotency_key = f"{REFUND_KEY_PREFIX}{order_id}"
    if is_done(redis, idempotency_key):
        logger.info("order %s already refunded (idempotent), skip", order_id)
        return True

    amount = float(amount_raw)
    user_id_int = int(user_id)

    try:
        order = Order.get(order_id)
    except NotFoundError:
        logger.warning("order not found for refund: %s", order_id)
        return True

    if order.status == ORDER_STATUS_REFUNDED:
        confirm(redis, idempotency_key)
        return True

    if not try_claim(redis, idempotency_key):
        logger.info("order %s refund already in progress, skip", order_id)
        return True

    try:
        _refund_user(user_id_int, amount)
        order.status = ORDER_STATUS_REFUNDED
        order.save()

        if product_id and quantity_raw:
            _release_stock(product_id, int(quantity_raw))

        confirm(redis, idempotency_key)
        logger.info(
            "refunded order %s user=%s amount=%s reason=%s",
            order_id,
            user_id_int,
            amount,
            reason,
        )
        return True
    except Exception:
        logger.exception("refund failed for order %s", order_id)
        release_claim(redis, idempotency_key)
        return False


def run_consumer(stop_event: Event, state: ConsumerState) -> None:
    redis = get_redis()
    _ensure_consumer_group(redis)
    state.thread_alive = True

    while not stop_event.is_set():
        state.heartbeat()
        try:
            messages = redis.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_KEY: ">"},
                count=10,
                block=2000,
            )
            if not messages:
                continue

            for _stream, entries in messages:
                for message_id, fields in entries:
                    if _handle_message(fields, redis):
                        redis.xack(STREAM_KEY, GROUP_NAME, message_id)
        except Exception:
            logger.exception("refund consumer loop error")
            time.sleep(1)
