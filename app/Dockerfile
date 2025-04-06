FROM python:3.11.3-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"


WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 5000


CMD  ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
