"""
Vercel Serverless Function entry point.
Wraps the FastAPI app for Vercel's Python runtime.
"""
import sys
import os

# Add the backend directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
