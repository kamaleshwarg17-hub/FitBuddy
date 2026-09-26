"""
FitBuddy Launcher Script
Run: python run.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print("=" * 60)
    print(">> STARTING FITBUDDY - AI FITNESS PLAN GENERATOR")
    print("=" * 60)
    print(f">> Local Web App:     http://{host}:{port}")
    print(f">> Interactive Docs:  http://{host}:{port}/docs")
    print(f">> Admin Dashboard:   http://{host}:{port}/view-all-users")
    print("=" * 60)
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
