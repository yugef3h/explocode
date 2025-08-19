import sys
import time
from concurrent import futures
from pathlib import Path
from threading import Event

import grpc

_DEMO_ROOT = Path(__file__).resolve().parents[3]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))

from product.v1 import product_pb2_grpc

from app.config import settings
from app.grpc_servicer import ProductServicer


def run_grpc_server(stop_event: Event) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductServicer(), server)
    address = f"[::]:{settings.grpc_port}"
    server.add_insecure_port(address)
    server.start()
    while not stop_event.is_set():
        time.sleep(0.5)
    server.stop(grace=5)
