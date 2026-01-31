#!/usr/bin/env python3
"""
Run script for Sarthi API
"""
import subprocess
import sys
import os

def main():
    """Run the Sarthi API server"""
    print("Starting Sarthi API server...")

    # Check if .env exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found. Please create it from .env.example")
        print("Continuing with default settings...")

    # Run uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"  # Enable auto-reload for development
    ]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down Sarthi API server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()