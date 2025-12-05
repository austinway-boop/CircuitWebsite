#!/usr/bin/env python3
"""
Black Magic Demo Application
Main entry point.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.web_app import run_app

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    run_app(host='127.0.0.1', port=2404, debug=True)
