import sys
from pathlib import Path

import grpc

_DEMO_ROOT = Path(__file__).resolve().parents[3]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))

from user.v1 import user_pb2, user_pb2_grpc

from app.schemas import UserCreate
from app.store import (
    InsufficientBalanceError,
    UserNotFoundError,
    charge_user,
    create_user,
    get_user,
    list_users,
    refund_user,
)


def _to_proto(user) -> user_pb2.User:
    return user_pb2.User(id=user.id, name=user.name, balance=user.balance)


class UserServicer(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        try:
            return _to_proto(get_user(request.user_id))
        except UserNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

    def ListUsers(self, request, context):
        return user_pb2.ListUsersResponse(users=[_to_proto(u) for u in list_users()])

    def CreateUser(self, request, context):
        user = create_user(
            UserCreate(name=request.name, balance=request.balance or 10000.0)
        )
        return _to_proto(user)

    def ChargeUser(self, request, context):
        try:
            return _to_proto(charge_user(request.user_id, request.amount))
        except UserNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        except InsufficientBalanceError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Insufficient balance")

    def RefundUser(self, request, context):
        try:
            return _to_proto(refund_user(request.user_id, request.amount))
        except UserNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

    def HealthCheck(self, request, context):
        return user_pb2.HealthCheckResponse(status="ok", service="user-service")
