
import sys
import os

# Add current directory to path so we can import backend
sys.path.append(os.getcwd())

try:
    print("Attempting to import backend.main...")
    import backend.main
    print("Successfully imported backend.main")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
