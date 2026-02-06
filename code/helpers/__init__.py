"""
Helper modules for Last.fm scrobble analysis.

This package provides utilities for:
- API interaction with Last.fm
- Data analysis and mood classification
- Report generation
- Visualization and graph generation
- Caching for performance
"""

from .api import fetch_scrobbles, fetch_artist_genres
from .analysis import classify_mood, group_scrobbles_by_month, analyze_months
from .cache import load_json_cache, save_json_cache
from .config import (
    LASTFM_API_URL, OUTPUT_DIR, WINDOW_SIZE,
    MOOD_MAPPINGS, MOOD_COLORS
)
from .reporting import generate_report, export_to_csv
from .visualization import GraphOptions, generate_graphs

__all__ = [
    # API
    "fetch_scrobbles",
    "fetch_artist_genres",
    # Analysis
    "classify_mood",
    "group_scrobbles_by_month",
    "analyze_months",
    # Cache
    "load_json_cache",
    "save_json_cache",
    # Config
    "LASTFM_API_URL",
    "OUTPUT_DIR",
    "WINDOW_SIZE",
    "MOOD_MAPPINGS",
    "MOOD_COLORS",
    # Reporting
    "generate_report",
    "export_to_csv",
    # Visualization
    "GraphOptions",
    "generate_graphs",
]
