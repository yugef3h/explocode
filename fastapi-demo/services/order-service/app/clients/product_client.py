import sys
from pathlib import Path

import grpc

from app.clients.grpc_errors import map_grpc_error
from app.config import settings

_DEMO_ROOT = Path(__file__).resolve().parents[4]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))

from product.v1 import product_pb2, product_pb2_grpc


async def get_product(product_id: str) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.a_service_grpc_target) as channel:
            stub = product_pb2_grpc.ProductServiceStub(channel)
            response = await stub.GetProduct(
                product_pb2.GetProductRequest(product_id=product_id),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="A service") from exc
    return {
        "id": response.id,
        "name": response.name,
        "price": response.price,
        "quantity": response.quantity,
    }


async def reserve_stock(product_id: str, quantity: int) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.a_service_grpc_target) as channel:
            stub = product_pb2_grpc.ProductServiceStub(channel)
            response = await stub.ReserveStock(
                product_pb2.ReserveStockRequest(
                    product_id=product_id,
                    quantity=quantity,
                ),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="A service") from exc
    return {"id": response.id, "quantity": response.quantity}


async def release_stock(product_id: str, quantity: int) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.a_service_grpc_target) as channel:
            stub = product_pb2_grpc.ProductServiceStub(channel)
            response = await stub.ReleaseStock(
                product_pb2.ReleaseStockRequest(
                    product_id=product_id,
                    quantity=quantity,
                ),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="A service") from exc
    return {"id": response.id, "quantity": response.quantity}


def release_stock_sync(product_id: str, quantity: int) -> None:
    with grpc.insecure_channel(settings.a_service_grpc_target) as channel:
        stub = product_pb2_grpc.ProductServiceStub(channel)
        stub.ReleaseStock(
            product_pb2.ReleaseStockRequest(
                product_id=product_id,
                quantity=quantity,
            ),
            timeout=5,
        )
