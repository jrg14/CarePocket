import sys

from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
backend_path = str(BACKEND)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
