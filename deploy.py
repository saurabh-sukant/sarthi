#!/usr/bin/env python3
"""
Deployment script for Sarthi system
Handles setup, running, and testing of the complete system
"""

import subprocess
import sys
import os
import time
import argparse
from pathlib import Path

def run_command(command: str, cwd: str = None, check: bool = True):
    """Run a shell command"""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def setup_environment():
    """Set up the Python environment"""
    print("🐍 Setting up Python environment...")

    # Check if virtual environment exists
    if not Path("venv").exists():
        print("Creating virtual environment...")
        # Use 'py' on Windows, 'python3' on Unix
        python_cmd = "py" if os.name == 'nt' else "python3"
        if not run_command(f"{python_cmd} -m venv venv"):
            return False

    # Activate virtual environment and install dependencies
    activate_cmd = ".\\venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"

    # Install dependencies
    pip_cmd = f"{activate_cmd} && python -m pip install --upgrade pip"
    if not run_command(pip_cmd):
        return False

    pip_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    if not run_command(pip_cmd):
        return False

    print("✅ Python environment setup complete")
    return True

def setup_frontend():
    """Set up the Next.js frontend"""
    print("⚛️ Setting up Next.js frontend...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    # Install dependencies
    if not run_command("npm install", cwd=str(frontend_dir)):
        return False

    print("✅ Frontend setup complete")
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")

    activate_cmd = ".\\venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"
    cmd = f"{activate_cmd} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

    print("Backend starting on http://localhost:8000")
    print("Press Ctrl+C to stop")

    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        return False

    return True

def start_frontend():
    """Start the Next.js frontend"""
    print("🌐 Starting Next.js frontend...")

    frontend_dir = Path("frontend")

    print("Frontend starting on http://localhost:3000")
    print("Press Ctrl+C to stop")

    try:
        subprocess.run("npm run dev", shell=True, cwd=str(frontend_dir), check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
        return False

    return True

def run_tests():
    """Run the comprehensive test suite"""
    print("🧪 Running system tests...")

    activate_cmd = ".\\venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"
    cmd = f"{activate_cmd} && python test_system.py"

    return run_command(cmd)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking system requirements...")

    # Check Python version
    try:
        result = subprocess.run([sys.executable, "--version"],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ Python: {version}")
    except subprocess.CalledProcessError:
        print("❌ Python not found")
        return False

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ Node.js: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found")
        return False

    # Check npm
    try:
        result = subprocess.run(["npm", "--version"],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ npm: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found")
        return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Sarthi Deployment Script")
    parser.add_argument("action", choices=["setup", "backend", "frontend", "full", "test"],
                       help="Action to perform")
    parser.add_argument("--skip-checks", action="store_true",
                       help="Skip system requirement checks")

    args = parser.parse_args()

    if not args.skip_checks and not check_requirements():
        print("❌ System requirements not met. Please install missing dependencies.")
        sys.exit(1)

    if args.action == "setup":
        print("🔧 Setting up Sarthi system...")

        if not setup_environment():
            print("❌ Environment setup failed")
            sys.exit(1)

        if not setup_frontend():
            print("❌ Frontend setup failed")
            sys.exit(1)

        print("✅ Setup complete! Run 'python deploy.py full' to start the system.")

    elif args.action == "backend":
        if not setup_environment():
            print("❌ Environment setup failed")
            sys.exit(1)

        start_backend()

    elif args.action == "frontend":
        if not setup_frontend():
            print("❌ Frontend setup failed")
            sys.exit(1)

        start_frontend()

    elif args.action == "full":
        print("🚀 Starting complete Sarthi system...")

        if not setup_environment():
            print("❌ Environment setup failed")
            sys.exit(1)

        if not setup_frontend():
            print("❌ Frontend setup failed")
            sys.exit(1)

        # Start backend in background
        print("Starting backend...")
        python_cmd = "py" if os.name == 'nt' else "python"
        backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "app.main:app",
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=os.getcwd()
        )

        # Wait a bit for backend to start
        time.sleep(3)

        # Start frontend
        print("Starting frontend...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(Path("frontend"))
        )

        print("\n🎉 Sarthi system is running!")
        print("📊 Backend API: http://localhost:8000")
        print("🌐 Frontend UI: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services")

        try:
            # Wait for both processes
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            print("✅ All services stopped")

    elif args.action == "test":
        if not setup_environment():
            print("❌ Environment setup failed")
            sys.exit(1)

        # Start backend for testing
        print("Starting backend for testing...")
        python_cmd = "py" if os.name == 'nt' else "python"
        backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "app.main:app",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=os.getcwd()
        )

        # Wait for backend to start
        time.sleep(3)

        try:
            # Run tests
            success = run_tests()
        finally:
            # Stop backend
            backend_process.terminate()
            backend_process.wait()

        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()