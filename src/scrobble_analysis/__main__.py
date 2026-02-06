"""
Entry point for running scrobble_analysis as a module.

Usage:
    python -m scrobble_analysis --username <username> --api-key <key>
    python -m scrobble_analysis -u <username> -k <key> --no-graphs
"""

from .cli import main

if __name__ == "__main__":
    main()
