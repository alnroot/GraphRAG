FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install debugpy

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY .env* .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "app.py"]
