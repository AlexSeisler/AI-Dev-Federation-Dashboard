# Use official Python base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache layer)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# ✅ Copy the whole server folder into /app/server
COPY . /app/server

EXPOSE 8080

# ✅ Now main.py is inside server/, so imports like "from server import ..." work
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
