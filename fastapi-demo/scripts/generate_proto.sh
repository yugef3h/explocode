#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROTO_DIR="$ROOT/proto"
OUT_DIR="$ROOT/gen/python"
VENV_PYTHON="${ROOT}/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Missing venv at $VENV_PYTHON — run: pnpm fastapi:install"
  exit 1
fi

mkdir -p "$OUT_DIR"
touch "$OUT_DIR/__init__.py"

"$VENV_PYTHON" -m grpc_tools.protoc \
  -I "$PROTO_DIR" \
  --python_out="$OUT_DIR" \
  --grpc_python_out="$OUT_DIR" \
  "$PROTO_DIR/user/v1/user.proto" \
  "$PROTO_DIR/product/v1/product.proto"

find "$OUT_DIR" -type d -exec touch {}/__init__.py \;

echo "Generated gRPC stubs under $OUT_DIR"
