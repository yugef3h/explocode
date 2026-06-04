import logging
import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings

os.environ["REDIS_OM_URL"] = settings.redis_om_url

from app.complete_scheduler import run_scheduler
from app.consumer import run_consumer
from app.consumer_state import ConsumerState
from app.redis_client import get_redis
from app.routers import orders
from redis_om import NotFoundError

logging.basicConfig(level=logging.INFO)


def _start_worker(name: str, target, stop_event: threading.Event, state: ConsumerState):
    thread = threading.Thread(
        target=target,
        args=(stop_event, state),
        name=name,
        daemon=True,
    )
    thread.start()
    return thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis()
    redis_client.ping()
    app.state.redis = redis_client

    stop_event = threading.Event()
    refund_state = ConsumerState(name="refund-consumer")
    scheduler_state = ConsumerState(name="complete-scheduler")

    refund_thread = _start_worker(
        "inventory-failed-consumer", run_consumer, stop_event, refund_state
    )
    scheduler_thread = _start_worker(
        "order-complete-scheduler", run_scheduler, stop_event, scheduler_state
    )

    app.state.consumer_stop_event = stop_event
    app.state.refund_state = refund_state
    app.state.scheduler_state = scheduler_state
    app.state.refund_thread = refund_thread
    app.state.scheduler_thread = scheduler_thread

    yield

    stop_event.set()
    refund_thread.join(timeout=5)
    scheduler_thread.join(timeout=5)
    redis_client.close()


app = FastAPI(title="Order Service", version="0.1.0", lifespan=lifespan)
app.include_router(orders.router)


@app.get("/health")
def health(request: Request) -> JSONResponse:
    request.app.state.redis.ping()
    refund_ok = request.app.state.refund_state.is_healthy()
    scheduler_ok = request.app.state.scheduler_state.is_healthy()
    consumers_ok = refund_ok and scheduler_ok

    body = {
        "status": "ok" if consumers_ok else "degraded",
        "service": "order-service",
        "redis": "ok",
        "consumers": {
            "refund": "ok" if refund_ok else "unhealthy",
            "complete_scheduler": "ok" if scheduler_ok else "unhealthy",
        },
    }
    status_code = 200 if consumers_ok else 503
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Order not found"})
