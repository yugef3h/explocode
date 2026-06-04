import httpx
from fastapi import HTTPException

from app.config import settings

_HTTPX_KWARGS = {"timeout": 5.0, "trust_env": False}


async def get_product(product_id: str) -> dict:
    url = f"{settings.a_service_url.rstrip('/')}/products/{product_id}"
    try:
        async with httpx.AsyncClient(**_HTTPX_KWARGS) as client:
            response = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"A service unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(status_code=400, detail="Product not found")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"A service error: {response.status_code}",
        )

    data = response.json()
    return {
        "id": data.get("id") or data.get("pk"),
        "name": data["name"],
        "price": data["price"],
        "quantity": data["quantity"],
    }


async def reserve_stock(product_id: str, quantity: int) -> dict:
    url = f"{settings.a_service_url.rstrip('/')}/products/{product_id}/reserve"
    try:
        async with httpx.AsyncClient(**_HTTPX_KWARGS) as client:
            response = await client.post(url, json={"quantity": quantity})
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"A service unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(status_code=400, detail="Product not found")
    if response.status_code == 409:
        raise HTTPException(status_code=400, detail="Insufficient product stock")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"A service error: {response.status_code}",
        )

    return response.json()


async def release_stock(product_id: str, quantity: int) -> dict:
    url = f"{settings.a_service_url.rstrip('/')}/products/{product_id}/release"
    try:
        async with httpx.AsyncClient(**_HTTPX_KWARGS) as client:
            response = await client.post(url, json={"quantity": quantity})
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"A service unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(status_code=400, detail="Product not found")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"A service error: {response.status_code}",
        )

    return response.json()
