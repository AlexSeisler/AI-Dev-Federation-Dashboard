# Use official Python image (pin to 3.11 to avoid 3.13 issues)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps for psycopg2 + other libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Expose Render’s expected port
EXPOSE 8080

# Start FastAPI with uvicorn
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
