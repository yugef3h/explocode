import logging
import time
from enum import Enum
from threading import Event

from redis.exceptions import ResponseError

from app.consumer_state import ConsumerState
from app.idempotency import is_fulfilled, mark_fulfilled
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

STREAM_KEY = "order_completed"
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


def _handle_message(fields: dict, redis) -> HandleResult:
    decoded = {_decode(k): _decode(v) for k, v in fields.items()}
    product_id = decoded.get("product_id")
    quantity = int(decoded.get("quantity", 0))
    order_id = decoded.get("pk")
    if not product_id or quantity <= 0:
        logger.warning("skip invalid message: %s", decoded)
        return HandleResult.ACK

    if order_id and is_fulfilled(redis, order_id):
        logger.info("duplicate order_completed for order %s, skip", order_id)
        return HandleResult.ACK

    if order_id:
        mark_fulfilled(redis, order_id)

    logger.info(
        "order %s fulfilled for product %s quantity %s",
        order_id,
        product_id,
        quantity,
    )
    return HandleResult.ACK


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
                    result = _handle_message(fields, redis)
                    if result is HandleResult.ACK:
                        redis.xack(STREAM_KEY, GROUP_NAME, message_id)
        except Exception:
            logger.exception("consumer loop error")
            time.sleep(1)
