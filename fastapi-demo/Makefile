.PHONY: install proto dev-user dev-order dev-a up down

GEN_PATH := gen/python
VENV := .venv/bin

install:
	$(VENV)/pip install -r services/user-service/requirements.txt
	$(VENV)/pip install -r services/order-service/requirements.txt
	$(VENV)/pip install -r services/a/requirements.txt
	$(VENV)/pip install grpcio-tools

proto:
	bash scripts/generate_proto.sh

dev-user:
	cd services/user-service && PYTHONPATH=../../$(GEN_PATH) ../../$(VENV)/python -m app.main

dev-order:
	cd services/order-service && PYTHONPATH=../../$(GEN_PATH) USER_SERVICE_GRPC_TARGET=127.0.0.1:50051 A_SERVICE_GRPC_TARGET=127.0.0.1:50053 ../../$(VENV)/uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

dev-a:
	cd services/a && PYTHONPATH=../../$(GEN_PATH) ../../$(VENV)/uvicorn app.main:app --reload --host 0.0.0.0 --port 8003

up:
	docker compose up --build

down:
	docker compose down
