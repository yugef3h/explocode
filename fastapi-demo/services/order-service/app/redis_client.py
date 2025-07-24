from redis_om import get_redis_connection

from app.config import settings


def get_redis():
    return get_redis_connection(url=settings.redis_om_url)
