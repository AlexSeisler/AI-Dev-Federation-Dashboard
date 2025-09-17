FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY server/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy code directly into /app
COPY server /app

EXPOSE 8080

# Run main.py directly (since it's now /app/main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
