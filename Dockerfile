# Stage 1: Build Frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Serve
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure logs are visible immediately
ENV PYTHONUNBUFFERED=1

# Copy Backend Code (Keep directory structure for imports)
COPY backend/ backend/

# Create data directory for SQLite persistence
RUN mkdir -p /app/data
ENV DB_DIR=/app/data

# Copy Built Frontend Assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose Port (Railway controls this, but good for doc)
EXPOSE 8000

# Set PYTHONPATH to /app so 'backend' package is found
ENV PYTHONPATH=/app

# Run Command (Run as module to ensure relative imports work)
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
