FROM python:3.10-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Command is handled by docker-compose, but providing default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
