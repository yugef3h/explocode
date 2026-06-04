DONE_TTL_SECONDS = 7 * 24 * 3600

FULFILLED_KEY_PREFIX = "order_fulfilled:"


def is_fulfilled(redis, order_id: str) -> bool:
    return bool(redis.exists(f"{FULFILLED_KEY_PREFIX}{order_id}"))


def mark_fulfilled(redis, order_id: str) -> bool:
    return bool(
        redis.set(
            f"{FULFILLED_KEY_PREFIX}{order_id}",
            "1",
            nx=True,
            ex=DONE_TTL_SECONDS,
        )
    )
