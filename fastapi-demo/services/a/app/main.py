import logging
import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi.responses import JSONResponse

_SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICE_ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

os.environ["REDIS_OM_URL"] = settings.redis_om_url

from app.consumer import run_consumer
from app.consumer_state import ConsumerState
from app.grpc_server import run_grpc_server
from app.models import Product
from app.redis_client import get_redis
from app.routers import hello
from app.schemas import ProductCreate
from redis_om import NotFoundError

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis()
    redis_client.ping()
    app.state.redis = redis_client

    stop_event = threading.Event()
    consumer_state = ConsumerState(name="order-completed-consumer")
    consumer_thread = threading.Thread(
        target=run_consumer,
        args=(stop_event, consumer_state),
        name="order-completed-consumer",
        daemon=True,
    )
    grpc_thread = threading.Thread(
        target=run_grpc_server,
        args=(stop_event,),
        name="product-grpc-server",
        daemon=True,
    )
    consumer_thread.start()
    grpc_thread.start()
    app.state.consumer_stop_event = stop_event
    app.state.consumer_state = consumer_state
    app.state.consumer_thread = consumer_thread
    app.state.grpc_thread = grpc_thread

    yield

    stop_event.set()
    consumer_thread.join(timeout=5)
    grpc_thread.join(timeout=5)
    redis_client.close()


app = FastAPI(title="A Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8002", "http://localhost:8003", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hello.router)


@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }


@app.get("/health")
def health(request: Request) -> JSONResponse:
    request.app.state.redis.ping()
    consumer_ok = request.app.state.consumer_state.is_healthy()
    body = {
        "status": "ok" if consumer_ok else "degraded",
        "service": "a-service",
        "redis": "ok",
        "consumers": {
            "order_completed": "ok" if consumer_ok else "unhealthy",
        },
    }
    status_code = 200 if consumer_ok else 503
    return JSONResponse(status_code=status_code, content=body)


@app.post("/products")
def create(payload: ProductCreate) -> Product:
    return Product(pk=None, **payload.model_dump()).save()


@app.get("/products/{pk}")
def get(pk: str) -> Product:
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
    try:
        Product.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    Product.delete(pk)
    return {"status": "ok", "message": "Product deleted successfully"}


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Product not found"})
