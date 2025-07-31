import logging
import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings

os.environ["REDIS_OM_URL"] = settings.redis_om_url

from redis_om import NotFoundError

from app.consumer import run_consumer
from app.redis_client import get_redis
from app.routers import orders

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis()
    redis_client.ping()
    app.state.redis = redis_client

    stop_event = threading.Event()
    consumer_thread = threading.Thread(
        target=run_consumer,
        args=(stop_event,),
        name="inventory-failed-consumer",
        daemon=True,
    )
    consumer_thread.start()
    app.state.consumer_stop_event = stop_event
    app.state.consumer_thread = consumer_thread

    yield

    stop_event.set()
    consumer_thread.join(timeout=5)
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
