"""Standalone server runner for Intelligent Financial Platform web app.
Usage:
    python run_app.py
"""
import os
import sys

# Set non-interactive Matplotlib backend BEFORE any matplotlib imports occur
import matplotlib
matplotlib.use('Agg')

# Ensure project root is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=================================================================")
    print(f" Starting Intelligent Financial Platform Web Application")
    print(f" Open your browser at: http://127.0.0.1:{port}")
    print(f" Press Ctrl+C in this terminal to stop the server")
    print(f"=================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
