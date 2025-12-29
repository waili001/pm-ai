import sys
import os

print(f"Python executable: {sys.executable}")
try:
    from fastapi import BackgroundTasks
    print("Successfully imported BackgroundTasks from fastapi")
except ImportError as e:
    print(f"Failed to import BackgroundTasks: {e}")

try:
    with open('backend/main.py', 'r') as f:
        content = f.read()
        print(f"First line of backend/main.py: {content.splitlines()[0]}")
except Exception as e:
    print(f"Failed to read backend/main.py: {e}")
