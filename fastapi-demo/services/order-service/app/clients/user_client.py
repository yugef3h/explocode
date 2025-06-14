import httpx
from fastapi import HTTPException

from app.config import settings


async def get_user(user_id: int) -> dict:
    url = f"{settings.user_service_url.rstrip('/')}/users/{user_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"User service unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(status_code=400, detail="User not found")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"User service error: {response.status_code}",
        )

    return response.json()
