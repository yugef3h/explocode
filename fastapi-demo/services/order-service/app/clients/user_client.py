import sys
from pathlib import Path

import grpc

from app.clients.grpc_errors import map_grpc_error
from app.config import settings

_DEMO_ROOT = Path(__file__).resolve().parents[4]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))

from user.v1 import user_pb2, user_pb2_grpc


def _user_to_dict(user: user_pb2.User) -> dict:
    return {"id": user.id, "name": user.name, "balance": user.balance}


async def get_user(user_id: int) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.user_service_grpc_target) as channel:
            stub = user_pb2_grpc.UserServiceStub(channel)
            response = await stub.GetUser(
                user_pb2.GetUserRequest(user_id=user_id),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="User service") from exc
    return _user_to_dict(response)


async def charge_user(user_id: int, amount: float) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.user_service_grpc_target) as channel:
            stub = user_pb2_grpc.UserServiceStub(channel)
            response = await stub.ChargeUser(
                user_pb2.ChargeUserRequest(user_id=user_id, amount=amount),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="User service") from exc
    return _user_to_dict(response)


async def refund_user(user_id: int, amount: float) -> dict:
    try:
        async with grpc.aio.insecure_channel(settings.user_service_grpc_target) as channel:
            stub = user_pb2_grpc.UserServiceStub(channel)
            response = await stub.RefundUser(
                user_pb2.RefundUserRequest(user_id=user_id, amount=amount),
                timeout=5,
            )
    except grpc.RpcError as exc:
        raise map_grpc_error(exc, service_name="User service") from exc
    return _user_to_dict(response)


def refund_user_sync(user_id: int, amount: float) -> None:
    with grpc.insecure_channel(settings.user_service_grpc_target) as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        stub.RefundUser(
            user_pb2.RefundUserRequest(user_id=user_id, amount=amount),
            timeout=5,
        )
