FROM python:3.12-slim

WORKDIR /app

COPY services/order-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gen/python ./gen/python
COPY services/order-service/app ./app

ENV PYTHONPATH=/app/gen/python
ENV ORDER_SERVICE_PORT=8002
ENV USER_SERVICE_GRPC_TARGET=user-service:50051
ENV A_SERVICE_GRPC_TARGET=a-service:50053

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${ORDER_SERVICE_PORT}"]
