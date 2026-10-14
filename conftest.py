"""Root conftest.py — adds project root to sys.path so `backend` is importable."""
import sys
import os

# Ensure the project root is on the path for all test modules.
sys.path.insert(0, os.path.dirname(__file__))
