import os

from fastapi import FastAPI

from app.config import settings
from app.routers import hello

os.environ.setdefault("REDIS_OM_URL", settings.redis_om_url)

app = FastAPI(title="A Service", version="0.1.0")
app.include_router(hello.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "a-service"}
