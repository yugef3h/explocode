import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis_om import NotFoundError, get_redis_connection

from app.config import settings
from app.routers import orders

os.environ.setdefault("REDIS_OM_URL", settings.redis_om_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis_connection(url=settings.redis_om_url)
    redis_client.ping()
    app.state.redis = redis_client
    yield
    redis_client.close()


app = FastAPI(title="Order Service", version="0.1.0", lifespan=lifespan)
app.include_router(orders.router)


@app.get("/health")
def health() -> dict[str, str]:
    app.state.redis.ping()
    return {"status": "ok", "service": "order-service", "redis": "ok"}


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Order not found"})
