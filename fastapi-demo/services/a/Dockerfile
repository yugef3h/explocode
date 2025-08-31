FROM python:3.12-slim

WORKDIR /app

COPY services/a/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gen/python ./gen/python
COPY services/a/app ./app

ENV PYTHONPATH=/app/gen/python
ENV A_SERVICE_PORT=8003
ENV GRPC_PORT=50053

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${A_SERVICE_PORT}"]
