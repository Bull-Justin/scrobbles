"""
Analysis functions for processing scrobble data.
"""

from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

from .config import MOOD_MAPPINGS, GENRE_CACHE_FILE
from .cache import load_json_cache, save_json_cache
from .api import fetch_artist_genres

__all__ = ["classify_mood", "group_scrobbles_by_month", "analyze_months"]

_KEYWORD_TO_MOOD: dict[str, str] = {}
for mood, keywords in MOOD_MAPPINGS.items():
    for keyword in keywords:
        _KEYWORD_TO_MOOD[keyword] = mood


@lru_cache(maxsize=1024)
def classify_mood(genres: tuple[str, ...]) -> str:
    """
    Classify mood based on genre tags

    Uses cached results for repeated genre combinations

    Args:
        genres: Tuple of genre strings (tuple for hashability)

    Returns:
        Mood string (e.g., "angsty", "dreamy", "neutral")
    """
    mood_scores: dict[str, int] = defaultdict(int)

    for genre in genres:
        genre_lower = genre.lower()
        if genre_lower in _KEYWORD_TO_MOOD:
            mood_scores[_KEYWORD_TO_MOOD[genre_lower]] += 1
        else:
            for keyword, mood in _KEYWORD_TO_MOOD.items():
                if keyword in genre_lower:
                    mood_scores[mood] += 1
                    break

    if mood_scores:
        return max(mood_scores, key=mood_scores.get)
    return "neutral"


def group_scrobbles_by_month(scrobbles: list[dict]) -> list[dict]:
    """
    Group scrobbles by month and year

    Args:
        scrobbles: List of scrobble dictionaries with 'timestamp' key

    Returns:
        List of month dictionaries sorted chronologically
    """
    monthly_data: dict[tuple[int, int], list[dict]] = defaultdict(list)

    for scrobble in scrobbles:
        dt = datetime.fromtimestamp(scrobble["timestamp"], tz=timezone.utc)
        key = (dt.year, dt.month)
        monthly_data[key].append(scrobble)

    return [
        {
            "month": month,
            "year": year,
            "tracks": tracks,
            "size": len(tracks)
        }
        for (year, month), tracks in sorted(monthly_data.items())
    ]


def analyze_months(months: list[dict], api_key: str) -> list[dict]:
    """
    Analyze monthly data and enrich with genre/mood data

    Args:
        months: List of month dictionaries from group_scrobbles_by_month
        api_key: Last.fm API key for fetching missing genre data

    Returns:
        Enriched list of month dictionaries with genre/mood analysis
    """
    print("\nFetching genre data from Last.fm")

    # Load genre cache
    genre_cache = load_json_cache(GENRE_CACHE_FILE)
    print(f"Genre cache: {len(genre_cache)} artists cached")

    # There is probably a better way to do this but I don't wanna
    all_artists: set[str] = {
        track["artist"]
        for month_data in months
        for track in month_data["tracks"]
    }
    print(f"Found {len(all_artists)} unique artists")

    uncached_artists = [a for a in all_artists if a.lower() not in genre_cache]
    for i, artist in enumerate(uncached_artists):
        print(f"  [{i + 1}/{len(uncached_artists)}] Fetching: {artist}")
        fetch_artist_genres(artist, api_key, genre_cache)

    if uncached_artists:
        save_json_cache(genre_cache, GENRE_CACHE_FILE)

    for month_data in months:
        genre_counts: dict[str, int] = defaultdict(int)
        mood_counts: dict[str, int] = defaultdict(int)

        for track in month_data["tracks"]:
            artist_genres = genre_cache.get(track["artist"].lower(), [])
            track["genres"] = artist_genres

            track["mood"] = classify_mood(tuple(artist_genres))

            # top 3 genres per track
            for genre in artist_genres[:3]:
                genre_counts[genre] += 1
            mood_counts[track["mood"]] += 1

        # top 10
        month_data["genre_distribution"] = dict(
            sorted(genre_counts.items(), key=lambda x: -x[1])[:10]
        )
        month_data["mood_distribution"] = dict(mood_counts)
        month_data["primary_mood"] = (
            max(mood_counts, key=mood_counts.get) if mood_counts else "unknown"
        )

    return months
