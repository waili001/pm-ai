#!/bin/bash

# Define ports
BACKEND_PORT=8000
FRONTEND_PORT=5173

echo "=================================================="
echo "Stopping existing services..."
echo "=================================================="

# Kill process on Backend Port
if lsof -ti:$BACKEND_PORT > /dev/null; then
    echo "Killing process on port $BACKEND_PORT..."
    lsof -ti:$BACKEND_PORT | xargs kill -9
else
    echo "No process found on port $BACKEND_PORT."
fi

# Kill process on Frontend Port
if lsof -ti:$FRONTEND_PORT > /dev/null; then
    echo "Killing process on port $FRONTEND_PORT..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9
else
    echo "No process found on port $FRONTEND_PORT."
fi

echo ""
echo "=================================================="
echo "Starting services..."
echo "=================================================="

# Start Backend
echo "Starting Backend..."
cd backend
# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Source .env if exists
    if [ -f ".env" ]; then
        echo "Loading .env variables..."
        set -a
        source .env
        set +a
    fi

    # Run in background with log redirection
    
    # Run in background with log redirection
    nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT > ../backend.log 2>&1 &
    echo "Backend started (PID: $!). Logs: backend.log"
else
    echo "Error: 'backend/venv' not found. Please setup python environment."
    exit 1
fi
cd ..

# Start Frontend
echo "Starting Frontend..."
cd frontend
# Run in background with log redirection
nohup npm run dev > ../frontend.log 2>&1 &
echo "Frontend started (PID: $!). Logs: frontend.log"
cd ..

echo ""
echo "=================================================="
echo "Done! Services are running in background."
echo "Access Frontend at: http://localhost:5173"
echo "Access Backend at: http://localhost:8000"
echo "=================================================="

tail -fn 100 backend.log