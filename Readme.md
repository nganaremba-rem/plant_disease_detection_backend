# FastAPI Image Processing Service Deployment Guide

This guide provides instructions for deploying the FastAPI image processing service to production.

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Your image processing model

## Setup

1. **Configure the service**:
   
   Edit `config.yaml` to match your environment:
   ```yaml
   input_dir: "data/input"
   output_dir: "data/output"
   model_path: "models/your_model.h5"
   # Other settings as needed
   ```

2. **Add your model**:
   
   Place your image processing model in the `models` directory as specified in the config.

3. **Customize the image processing logic**:
   
   In `main.py`, replace the placeholder `process_image` function with your actual image processing code.

## Deployment Options

### Option 1: Deploy with Docker

```bash
# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option 2: Deploy directly (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

## Using the API

Send image processing requests to the API:

```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/process/
```

## Health Check

The service includes a health check endpoint at `/health/` that can be used by monitoring tools or container orchestration platforms.

## Customization

The placeholder image processing code in `process_image()` function should be replaced with your actual image processing logic.