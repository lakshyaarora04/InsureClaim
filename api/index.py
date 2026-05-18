"""
Vercel serverless entrypoint for the FastAPI application.
"""
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH for backend imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mangum import Mangum
from backend.api.main import app

handler = Mangum(app, lifespan="off")
