#!/usr/bin/env python3
"""
Run the blackmagic web application
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.web_app import app, run_app

# Export app for Vercel serverless deployment
app = app

if __name__ == '__main__':
    print()
    print("  blackmagic v1.0")
    print("  ---------------")
    print("  http://localhost:2404")
    print()
    
    try:
        run_app(host='127.0.0.1', port=2404, debug=True)
    except KeyboardInterrupt:
        print("\n  stopped.")
        sys.exit(0)
