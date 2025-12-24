# PM-AI Project

This project uses a React frontend (with MUI) and a Python FastAPI backend.

## Prerequisites

- Node.js and npm
- Python 3.x

## Project Structure

- `frontend/`: React application
- `backend/`: FastAPI application

## Getting Started

### 1. Backend Setup

Navigate to the `backend` directory:

```bash
cd backend
```

Create and activate a virtual environment (if not already done):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 2. Frontend Setup

Open a new terminal and navigate to the `frontend` directory:

```bash
cd frontend
```

Install dependencies (if not already done):

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open your browser and navigate to the URL shown (usually `http://localhost:5173`). You should see the application fetching data from the backend.
