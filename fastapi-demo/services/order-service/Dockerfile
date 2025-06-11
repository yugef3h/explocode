FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV ORDER_SERVICE_PORT=8002
ENV USER_SERVICE_URL=http://user-service:8001

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${ORDER_SERVICE_PORT}"]
