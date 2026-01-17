FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY config/ /app/config/
COPY .env.example /app/.env

RUN mkdir -p /app/{data,logs}

CMD ["python", "src/main.py"]
