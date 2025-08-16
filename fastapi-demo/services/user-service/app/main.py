import asyncio
import logging

import grpc

from app.config import settings
from app.grpc_servicer import UserServicer

logger = logging.getLogger(__name__)


async def serve() -> None:
    from user.v1 import user_pb2_grpc

    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    address = f"[::]:{settings.grpc_port}"
    server.add_insecure_port(address)
    await server.start()
    logger.info("user-service gRPC listening on %s", address)
    await server.wait_for_termination()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())


if __name__ == "__main__":
    main()
