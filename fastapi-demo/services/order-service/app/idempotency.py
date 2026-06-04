DONE_TTL_SECONDS = 7 * 24 * 3600
CLAIM_TTL_SECONDS = 3600


def try_claim(redis, key: str) -> bool:
    return bool(redis.set(key, "processing", nx=True, ex=CLAIM_TTL_SECONDS))


def confirm(redis, key: str) -> None:
    redis.set(key, "done", ex=DONE_TTL_SECONDS)


def release_claim(redis, key: str) -> None:
    redis.delete(key)


def is_done(redis, key: str) -> bool:
    return bool(redis.exists(key))
