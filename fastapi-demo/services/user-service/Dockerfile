FROM python:3.12-slim

WORKDIR /app

COPY services/user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gen/python ./gen/python
COPY services/user-service/app ./app

ENV PYTHONPATH=/app/gen/python
ENV GRPC_PORT=50051

CMD ["python", "-m", "app.main"]
