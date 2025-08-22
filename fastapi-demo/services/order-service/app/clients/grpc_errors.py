import sys
from pathlib import Path

import grpc
from fastapi import HTTPException

_DEMO_ROOT = Path(__file__).resolve().parents[4]
if str(_DEMO_ROOT / "gen" / "python") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT / "gen" / "python"))


def map_grpc_error(exc: grpc.RpcError, *, service_name: str) -> HTTPException:
    code = exc.code()
    detail = exc.details() or f"{service_name} error"

    if code == grpc.StatusCode.NOT_FOUND:
        return HTTPException(status_code=400, detail=detail)
    if code == grpc.StatusCode.FAILED_PRECONDITION:
        return HTTPException(status_code=400, detail=detail)
    if code == grpc.StatusCode.UNAVAILABLE:
        return HTTPException(status_code=503, detail=f"{service_name} unavailable")
    return HTTPException(status_code=502, detail=detail)
