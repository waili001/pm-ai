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

# Copy Backend Code
COPY backend/ ./

# Create data directory for SQLite persistence
RUN mkdir -p /app/data
ENV DB_DIR=/app/data

# Copy Built Frontend Assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Expose Port (Railway controls this, but good for doc)
EXPOSE 8000

# Run Command (Use shell to interpolate PORT env var for Railway)
CMD ["sh", "-c", "python scripts/rename_legacy_tables.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
