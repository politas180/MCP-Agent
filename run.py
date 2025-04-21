#!/usr/bin/env python
"""
Run script for the MCP Agent Web Application.
This script starts the backend server and opens the frontend in a web browser.
"""
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_conda_env():
    """Check if we're running in the correct conda environment."""
    if os.environ.get('CONDA_DEFAULT_ENV') != 'mcp':
        print("Warning: You are not running in the 'mcp' conda environment.")
        print("It's recommended to run this application in the 'mcp' environment.")
        print("Run 'conda activate mcp' before running this script.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

def start_backend():
    """Start the Flask backend server."""
    print("Starting backend server...")
    backend_dir = Path(__file__).parent / 'backend'
    backend_path = backend_dir / 'app.py'

    # Use Python executable from current environment
    python_exe = sys.executable

    # Set the working directory to the backend directory
    # This ensures imports work correctly

    # Start the backend process
    backend_process = subprocess.Popen(
        [python_exe, str(backend_path)],
        cwd=str(backend_dir),  # Set working directory
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for the server to start
    time.sleep(2)

    # Check if the process is still running
    if backend_process.poll() is not None:
        print("Error: Backend server failed to start.")
        stdout, stderr = backend_process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        sys.exit(1)

    print("Backend server started on http://localhost:5000")
    return backend_process

def open_frontend():
    """Open the frontend in the default web browser."""
    print("Opening frontend in web browser...")
    frontend_path = Path(__file__).parent / 'frontend' / 'index.html'
    frontend_url = f"file://{frontend_path.absolute()}"
    webbrowser.open(frontend_url)

def main():
    """Main function to run the application."""
    print("MCP Agent Web Application")
    print("========================")

    # Check conda environment
    check_conda_env()

    # Start backend
    backend_process = start_backend()

    try:
        # Open frontend
        open_frontend()

        print("\nPress Ctrl+C to stop the server...")
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        # Terminate the backend process
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
