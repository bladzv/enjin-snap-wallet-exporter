#!/usr/bin/env python3
"""
Offline Server Runner for Enjin Snap Wallet Exporter

This script starts a local HTTP server to serve the Enjin Snap Exporter HTML interface
for offline use. It serves the files from the repository root directory.

Requirements:
- Python 3.6+ (for http.server module)
- Run this script from the scripts/ directory or repository root

Usage:
    python3 scripts/serve_offline.py
    # or from scripts/ directory:
    python3 serve_offline.py
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True

def find_python_command():
    """Find the appropriate python command to use for the server."""
    # Try python3 first, then python
    for cmd in ['python3', 'python']:
        if shutil.which(cmd):
            # Check if it's Python 3
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    return cmd
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
    return None

def main():
    print(__doc__)

    if not check_python_version():
        sys.exit(1)

    # Change to repository root if running from scripts/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    if os.path.basename(script_dir) == 'scripts':
        os.chdir(repo_root)
        print(f"Changed working directory to: {repo_root}")

    # Check if index.html exists
    if not os.path.exists('index.html'):
        print("Error: index.html not found in the current directory.")
        print("Please run this script from the repository root or scripts/ directory.")
        sys.exit(1)

    python_cmd = find_python_command()
    if not python_cmd:
        print("Error: Could not find Python 3 command.")
        sys.exit(1)

    print(f"Using Python command: {python_cmd}")
    print()
    print("This will start a local HTTP server on http://127.0.0.1:8000")
    print("Open http://127.0.0.1:8000/index.html in your browser")
    print("Press Ctrl+C to stop the server")
    print()

    try:
        response = input("Do you want to start the server? (y/N): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)

    if response not in ('y', 'yes'):
        print("Server not started.")
        sys.exit(0)

    print("Starting server...")
    try:
        # Run the server
        subprocess.run([
            python_cmd, '-m', 'http.server', '8000',
            '--bind', '127.0.0.1'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()