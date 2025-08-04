from redis_om import NotFoundError

from app.models import Product
from app.redis_client import get_redis

RESERVE_LUA = """
if redis.call('EXISTS', KEYS[1]) == 0 then return -1 end
local current = tonumber(redis.call('HGET', KEYS[1], 'quantity'))
if current == nil then return -1 end
local qty = tonumber(ARGV[1])
if current < qty then return 0 end
local remaining = current - qty
redis.call('HSET', KEYS[1], 'quantity', tostring(remaining))
return remaining
"""

RELEASE_LUA = """
if redis.call('EXISTS', KEYS[1]) == 0 then return -1 end
local current = tonumber(redis.call('HGET', KEYS[1], 'quantity'))
if current == nil then return -1 end
local qty = tonumber(ARGV[1])
local remaining = current + qty
redis.call('HSET', KEYS[1], 'quantity', tostring(remaining))
return remaining
"""


class InsufficientStockError(Exception):
    pass


def _product_redis_key(product_id: str) -> str:
    # redis-om HashModel key layout for Product
    return f"product:app.models.Product:{product_id}"


def reserve_stock(product_id: str, quantity: int) -> int:
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    redis = get_redis()
    result = redis.eval(RESERVE_LUA, 1, _product_redis_key(product_id), quantity)
    if result == -1:
        raise NotFoundError(f"Product {product_id} not found")
    if result == 0:
        raise InsufficientStockError(
            f"insufficient stock for product {product_id}"
        )
    return int(result)


def release_stock(product_id: str, quantity: int) -> int:
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    redis = get_redis()
    result = redis.eval(RELEASE_LUA, 1, _product_redis_key(product_id), quantity)
    if result == -1:
        raise NotFoundError(f"Product {product_id} not found")
    return int(result)
