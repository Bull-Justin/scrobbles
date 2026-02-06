"""
Scrobble Analysis - Last.fm listening habits analyzer.

This package provides utilities for:
- API interaction with Last.fm
- Data analysis and mood classification
- Report generation
- Visualization and graph generation
- Caching for performance
"""

from .analysis import analyze_months, classify_mood, group_scrobbles_by_month
from .api import fetch_artist_genres, fetch_scrobbles
from .cache import load_json_cache, save_json_cache
from .config import (
    LASTFM_API_URL,
    MOOD_COLORS,
    MOOD_MAPPINGS,
    OUTPUT_DIR,
    PROJECT_ROOT,
    WINDOW_SIZE,
)
from .reporting import export_to_csv, generate_report
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
    "PROJECT_ROOT",
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
