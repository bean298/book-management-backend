# Dockerfile: build docker image for this project
# User Multi-stage build method:
#   In first stage install all dependencies from requirement.txt
#   In second stage copy installed package from first stage, copy source code , open port 8000
# To build docker image from this file: docker build -t fastapi-book-management .
# Help docker to container and run only one app - FastAPI

# Multi-stage build

# ───────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies, packages
# ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Every command will run in folder app
WORKDIR /app

# Copy file requirements.txt from computer host into container
COPY requirements.txt .

# Install dependencies (--no-cache-dir dont save cache -> lighter)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────
# Stage 2: Runtime - final image to run app
# ──────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy packages Python from stage builder (Stage 1)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY . .

# Init port 8000
EXPOSE 8000

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]