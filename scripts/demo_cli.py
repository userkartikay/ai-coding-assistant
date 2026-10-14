"""Convenience launcher for Socratic DSA CLI."""
import sys
import os
import asyncio
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.cli.interactive_cli import run_terminal_session

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trusted local mentor prototype; no secure code sandbox')
    parser.add_argument('--trusted-local', action='store_true', help='Enable execution ONLY for code you authored or reviewed and trust')
    args = parser.parse_args()
    asyncio.run(run_terminal_session(trusted_local_code=args.trusted_local))
