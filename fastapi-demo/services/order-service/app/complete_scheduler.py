import logging
import time
from threading import Event

from redis_om import NotFoundError

from app.consumer_state import ConsumerState
from app.idempotency import confirm, is_done, release_claim, try_claim
from app.models import ORDER_STATUS_COMPLETED, Order
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

SCHEDULE_KEY = "order_complete_schedule"
PUBLISH_KEY_PREFIX = "order_complete_published:"
COMPLETE_DELAY_SECONDS = 2


def schedule_order_complete(order_pk: str) -> None:
    redis = get_redis()
    run_at = time.time() + COMPLETE_DELAY_SECONDS
    redis.zadd(SCHEDULE_KEY, {order_pk: run_at})
    logger.info("scheduled order %s complete at %s", order_pk, run_at)


def _publish_order_completed(order_pk: str) -> None:
    redis = get_redis()
    idempotency_key = f"{PUBLISH_KEY_PREFIX}{order_pk}"
    if is_done(redis, idempotency_key):
        return
    if not try_claim(redis, idempotency_key):
        return

    try:
        order = Order.get(order_pk)
    except NotFoundError:
        release_claim(redis, idempotency_key)
        return

    if order.status == ORDER_STATUS_COMPLETED:
        confirm(redis, idempotency_key)
        return

    order.status = ORDER_STATUS_COMPLETED
    order.save()
    fields = {
        key: str(value)
        for key, value in order.model_dump().items()
        if value is not None
    }
    redis.xadd("order_completed", fields)
    confirm(redis, idempotency_key)
    logger.info("published order_completed for order %s", order_pk)


def run_scheduler(stop_event: Event, state: ConsumerState) -> None:
    state.thread_alive = True
    while not stop_event.is_set():
        state.heartbeat()
        try:
            redis = get_redis()
            now = time.time()
            due = redis.zrangebyscore(SCHEDULE_KEY, 0, now, start=0, num=10)
            for raw_pk in due:
                order_pk = raw_pk.decode() if isinstance(raw_pk, bytes) else raw_pk
                try:
                    _publish_order_completed(order_pk)
                    redis.zrem(SCHEDULE_KEY, order_pk)
                except Exception:
                    logger.exception("failed to complete order %s", order_pk)
        except Exception:
            logger.exception("complete scheduler loop error")
        time.sleep(0.5)
