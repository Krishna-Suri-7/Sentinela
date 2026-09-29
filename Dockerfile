FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for building packages like psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (Render automatically assigns PORT)
EXPOSE 8000

# Command to run FastAPI server
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
