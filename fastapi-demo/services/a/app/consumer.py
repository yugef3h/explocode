import logging
import time
from threading import Event

from redis.exceptions import ResponseError
from redis_om import NotFoundError

from app.models import Product
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

STREAM_KEY = "order_completed"
GROUP_NAME = "a-service"
CONSUMER_NAME = "inventory-worker"


def _decode(value):
    return value.decode() if isinstance(value, bytes) else value


def _ensure_consumer_group(redis) -> None:
    try:
        redis.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def _handle_message(fields: dict) -> None:
    # items 把字典转成元组
    decoded = {_decode(k): _decode(v) for k, v in fields.items()}
    product_id = decoded.get("product_id")
    quantity = int(decoded.get("quantity", 0))
    if not product_id or quantity <= 0:
        logger.warning("skip invalid message: %s", decoded)
        return

    try:
        product = Product.get(product_id)
    except NotFoundError:
        logger.warning("product not found: %s", product_id)
        return

    if product.quantity < quantity:
        logger.warning(
            "insufficient stock for product %s: have %s, need %s",
            product_id,
            product.quantity,
            quantity,
        )
        return

    product.quantity -= quantity
    product.save()
    logger.info(
        "deducted %s from product %s, remaining %s",
        quantity,
        product_id,
        product.quantity,
    )


def run_consumer(stop_event: Event) -> None:
    redis = get_redis()
    _ensure_consumer_group(redis)

    while not stop_event.is_set():
        try:
            messages: list[tuple[str, list[tuple[str, dict]]]] = redis.xreadgroup(
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
                    _handle_message(fields)
                    redis.xack(STREAM_KEY, GROUP_NAME, message_id)
        except Exception:
            logger.exception("consumer loop error")
            time.sleep(1)
