"""Renamed: scripts/check_sources.py checks links, made-up addresses and quotes. This runs it with the same arguments."""
import os
import sys

os.execv(sys.executable, [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_sources.py'), *sys.argv[1:]])
