"""
Textora AI - Local Server Runner
Launches the FastAPI application using uvicorn on http://127.0.0.1:8000
"""
import sys
import uvicorn
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("=" * 60)
    print("Textora AI — Intelligent Text Audit Platform")
    print("Starting local server at: http://127.0.0.1:8000")
    print("Press Ctrl+C to terminate the server.")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
