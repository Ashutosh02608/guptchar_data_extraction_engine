"""
Vercel Serverless Function Entrypoint for Guptchar Core Data Extraction Engine.
Exposes the FastAPI ASGI application for Vercel's Python runtime.
"""

import os
import sys

# Ensure project root directory is added to sys.path so guptchar package imports resolve properly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from guptchar.api.server import app
