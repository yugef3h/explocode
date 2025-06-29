from fastapi import APIRouter

from app.schemas import HelloResponse

router = APIRouter(tags=["hello"])


@router.get("/", response_model=HelloResponse)
async def root() -> HelloResponse:
    return HelloResponse(message="Hello, World!")
