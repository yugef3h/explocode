from fastapi import FastAPI

from app.routers import orders

app = FastAPI(title="Order Service", version="0.1.0")
app.include_router(orders.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "order-service"}
