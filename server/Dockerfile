# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for psycopg2 and others)
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy server code (everything in /server context)
COPY . /app

# Expose port for Render
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
