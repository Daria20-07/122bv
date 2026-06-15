"""
Database package initialization.
"""

from .backend import memory
from .tui import TUI


def run():
    """Entry point for the database application."""
    app = TUI()
    app.run()


__all__ = ['memory', 'run', 'TUI']