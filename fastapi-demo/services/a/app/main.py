import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi.responses import JSONResponse

_SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(_SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICE_ROOT))

from fastapi import FastAPI, HTTPException, Request

from app.config import settings
from app.routers import hello
from app.schemas import ProductCreate

os.environ.setdefault("REDIS_OM_URL", settings.redis_om_url)

from redis_om import NotFoundError, get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware





@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = get_redis_connection(url=settings.redis_om_url)
    redis_client.ping()
    app.state.redis = redis_client
    yield
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


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        global_key_prefix = "product"


@app.get("/products")
def all():
    # get all products
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
def health() -> dict[str, str]:
    app.state.redis.ping()
    return {"status": "ok", "service": "a-service", "redis": "ok"}

@app.post("/products")
def create(payload: ProductCreate) -> Product:
    # ** 解包字典，json 转字典为 model_dump
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

# 全局捕获异常
@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Product not found"})