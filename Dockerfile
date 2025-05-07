# Builder stage for installing dependencies
FROM python:3.10.17-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create filtered requirements - exclude torch, torchvision and transformers
RUN grep -v "torch\|torchvision\|transformers" requirements.txt > requirements_base.txt || true

# Install base requirements first (smaller packages)
RUN pip install --no-cache-dir -r requirements_base.txt

# Install PyTorch separately (large package)
RUN pip install --no-cache-dir torch==2.6.0

# Install torchvision separately
RUN pip install --no-cache-dir torchvision==0.21.0

# Install transformers separately (also large)
RUN pip install --no-cache-dir transformers==4.50.3

# Final stage - copy only necessary files
FROM python:3.10.17-slim

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/input data/output models

# Expose the port
EXPOSE 8000

CMD ["python", "main.py"]
