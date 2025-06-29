from fastapi import FastAPI

from app.routers import hello

app = FastAPI(title="A Service", version="0.1.0")
app.include_router(hello.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "a-service"}
