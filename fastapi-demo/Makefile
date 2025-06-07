.PHONY: install dev-user dev-order up down

install:
	pip install -r services/user-service/requirements.txt
	pip install -r services/order-service/requirements.txt

dev-user:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 --app-dir services/user-service

dev-order:
	USER_SERVICE_URL=http://127.0.0.1:8001 uvicorn app.main:app --reload --host 0.0.0.0 --port 8002 --app-dir services/order-service

up:
	docker compose up --build

down:
	docker compose down
