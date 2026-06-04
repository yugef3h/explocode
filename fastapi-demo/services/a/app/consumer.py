import logging
import time
from enum import Enum
from threading import Event

from redis.exceptions import ResponseError
from redis_om import NotFoundError

from app.models import Product
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

STREAM_KEY = "order_completed"
INVENTORY_FAILED_STREAM = "inventory_failed"
GROUP_NAME = "a-service"
CONSUMER_NAME = "inventory-worker"


class HandleResult(str, Enum):
    ACK = "ack"
    NO_ACK = "no_ack"


def _decode(value):
    return value.decode() if isinstance(value, bytes) else value


def _ensure_consumer_group(redis) -> None:
    try:
        redis.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def _publish_inventory_failed(redis, decoded: dict, reason: str) -> None:
    order_id = decoded.get("pk")
    if not order_id:
        logger.warning("skip inventory_failed publish, missing order pk: %s", decoded)
        return

    fields = {
        "order_id": str(order_id),
        "user_id": str(decoded.get("user_id", "")),
        "amount": str(decoded.get("amount", "")),
        "product_id": str(decoded.get("product_id", "")),
        "quantity": str(decoded.get("quantity", "")),
        "reason": reason,
    }
    redis.xadd(INVENTORY_FAILED_STREAM, fields)
    logger.info("published inventory_failed for order %s reason=%s", order_id, reason)


def _handle_message(fields: dict, redis) -> HandleResult:
    decoded = {_decode(k): _decode(v) for k, v in fields.items()}
    product_id = decoded.get("product_id")
    quantity = int(decoded.get("quantity", 0))
    if not product_id or quantity <= 0:
        logger.warning("skip invalid message: %s", decoded)
        return HandleResult.ACK

    try:
        product = Product.get(product_id)
    except NotFoundError:
        logger.warning("product not found: %s", product_id)
        _publish_inventory_failed(redis, decoded, "product_not_found")
        return HandleResult.ACK

    if product.quantity < quantity:
        logger.warning(
            "insufficient stock for product %s: have %s, need %s",
            product_id,
            product.quantity,
            quantity,
        )
        _publish_inventory_failed(redis, decoded, "insufficient_stock")
        return HandleResult.ACK

    try:
        product.quantity -= quantity
        product.save()
    except Exception:
        logger.exception("failed to deduct inventory for product %s", product_id)
        return HandleResult.NO_ACK

    logger.info(
        "deducted %s from product %s, remaining %s",
        quantity,
        product_id,
        product.quantity,
    )
    return HandleResult.ACK


def run_consumer(stop_event: Event) -> None:
    redis = get_redis()
    _ensure_consumer_group(redis)

    while not stop_event.is_set():
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
                    result = _handle_message(fields, redis)
                    if result is HandleResult.ACK:
                        redis.xack(STREAM_KEY, GROUP_NAME, message_id)
        except Exception:
            logger.exception("consumer loop error")
            time.sleep(1)
