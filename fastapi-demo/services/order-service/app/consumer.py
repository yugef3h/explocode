import logging
import time
from threading import Event

import httpx
from redis.exceptions import ResponseError
from redis_om import NotFoundError

from app.config import settings
from app.models import ORDER_STATUS_REFUNDED, Order
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

STREAM_KEY = "inventory_failed"
GROUP_NAME = "order-service"
CONSUMER_NAME = "refund-worker"


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
    # trust_env=False 是告诉 httpx：不要读取系统/环境变量里的代理配置（如 HTTP_PROXY、HTTPS_PROXY、ALL_PROXY 等）。
    # 本地联调时我们遇到过这个问题：
    # curl http://127.0.0.1:8001/users/1 → 200 正常
    # httpx.get("http://127.0.0.1:8001/users/1") → 502 空响应
    # 原因是 macOS / 终端里往往配了代理（Clash、Surge 等），httpx 默认 trust_env=True，会把 127.0.0.1 的请求也走代理，代理处理不了本地服务就返回 502。
    # 加上 trust_env=False 后，httpx 直连目标地址，绕开代理。
    # 生产环境如果必须走公司代理访问外网，就不能全局关掉；可以只对内网 URL 禁用代理，或单独配置 proxies={}。
    with httpx.Client(timeout=5.0, trust_env=False) as client:
        response = client.post(url, json={"amount": amount})
    if response.status_code >= 400:
        raise RuntimeError(
            f"refund failed for user {user_id}: HTTP {response.status_code}"
        )


def _handle_message(fields: dict) -> bool:
    decoded = {_decode(k): _decode(v) for k, v in fields.items()}
    order_id = decoded.get("order_id")
    user_id = decoded.get("user_id")
    amount_raw = decoded.get("amount")
    reason = decoded.get("reason", "unknown")

    if not order_id or not user_id or not amount_raw:
        logger.warning("skip invalid inventory_failed message: %s", decoded)
        return True

    amount = float(amount_raw)
    user_id_int = int(user_id)

    try:
        order = Order.get(order_id)
    except NotFoundError:
        logger.warning("order not found for refund: %s", order_id)
        return True

    if order.status == ORDER_STATUS_REFUNDED:
        logger.info("order %s already refunded, skip", order_id)
        return True

    try:
        _refund_user(user_id_int, amount)
    except Exception:
        logger.exception("refund call failed for order %s", order_id)
        return False

    order.status = ORDER_STATUS_REFUNDED
    order.save()
    logger.info(
        "refunded order %s user=%s amount=%s reason=%s",
        order_id,
        user_id_int,
        amount,
        reason,
    )
    return True


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
                    if _handle_message(fields):
                        redis.xack(STREAM_KEY, GROUP_NAME, message_id)
        except Exception:
            logger.exception("refund consumer loop error")
            time.sleep(1)
