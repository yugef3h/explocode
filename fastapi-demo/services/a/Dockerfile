FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV A_SERVICE_PORT=8003

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${A_SERVICE_PORT}"]
