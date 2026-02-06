"""
Configuration and constants for scrobble analysis.
"""

from pathlib import Path

__all__ = [
    "LASTFM_API_URL",
    "BASE_DIR",
    "GENRE_CACHE_FILE",
    "SCROBBLE_CACHE_FILE",
    "OUTPUT_DIR",
    "WINDOW_SIZE",
    "MOOD_MAPPINGS",
    "MOOD_COLORS",
]

LASTFM_API_URL: str = "http://ws.audioscrobbler.com/2.0/"

BASE_DIR: Path = Path(__file__).parent.parent.parent
GENRE_CACHE_FILE: Path = BASE_DIR / "genre_cache.json"
SCROBBLE_CACHE_FILE: Path = BASE_DIR / "scrobble_cache.json"
OUTPUT_DIR: Path = BASE_DIR / "scrobble_analysis"

# I've just always used 80 for console output width, can't remember why
WINDOW_SIZE: int = 80

MOOD_MAPPINGS: dict[str, list[str]] = {
    "angsty": [
        "emo",
        "post-hardcore",
        "screamo",
        "midwest emo",
        "emo revival",
        "pop punk",
        "punk rock",
        "skate punk",
        "easycore",
    ],
    "introspective": [
        "folk",
        "singer-songwriter",
        "acoustic",
        "indie folk",
        "chamber pop",
        "baroque pop",
        "art pop",
        "freak folk",
    ],
    "dreamy": [
        "shoegaze",
        "dream pop",
        "ethereal",
        "ambient",
        "space rock",
        "chillwave",
        "synthwave",
        "vaporwave",
        "downtempo",
    ],
    "aggressive": [
        "metal",
        "hardcore",
        "death metal",
        "black metal",
        "grindcore",
        "noise rock",
        "sludge",
        "powerviolence",
        "mathcore",
        "thrash",
    ],
    "danceable": [
        "pop",
        "dance",
        "disco",
        "funk",
        "house",
        "edm",
        "synth pop",
        "electropop",
        "nu disco",
        "indie dance",
    ],
    "melancholic": [
        "slowcore",
        "sadcore",
        "doom",
        "depressive",
        "gothic",
        "dark",
        "funeral doom",
        "dsbm",
        "post-punk",
    ],
    "chaotic": [
        "math rock",
        "noise",
        "experimental",
        "avant-garde",
        "art rock",
        "no wave",
        "free jazz",
        "industrial",
        "glitch",
    ],
    "nostalgic": [
        "80s",
        "90s",
        "retro",
        "classic rock",
        "oldies",
        "vintage",
        "throwback",
        "britpop",
        "new wave",
        "post-punk revival",
    ],
    "warm": [
        "lo-fi",
        "lofi",
        "bedroom pop",
        "soft",
        "mellow",
        "cozy",
        "easy listening",
        "bossa nova",
        "smooth",
    ],
    "energetic": [
        "rock",
        "indie rock",
        "alternative rock",
        "garage rock",
        "hard rock",
        "stoner rock",
        "grunge",
        "power pop",
    ],
}

MOOD_COLORS: dict[str, str] = {
    "angsty": "#e74c3c",
    "introspective": "#8e44ad",
    "dreamy": "#9b59b6",
    "aggressive": "#c0392b",
    "danceable": "#f1c40f",
    "melancholic": "#34495e",
    "chaotic": "#e67e22",
    "nostalgic": "#1abc9c",
    "warm": "#3498db",
    "energetic": "#2ecc71",
    "neutral": "#95a5a6",
}
