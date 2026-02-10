"""Shared fixtures and dummy data for tests.

Dummy data modeled after the real scrobble_cache.json and genre_cache.json formats.
"""

import pytest


@pytest.fixture
def sample_scrobbles():
    """Scrobbles spanning two months across two years, modeled after real cache data."""
    return [
        {
            "track": "Satellite",
            "artist": "Stand Atlantic",
            "album": "Pink Elephant",
            "timestamp": 1703980800,  # 2023-12-31 00:00:00 UTC
            "date": "2023-12-31 00:00:00",
        },
        {
            "track": "Molasses",
            "artist": "Stand Atlantic",
            "album": "Pink Elephant",
            "timestamp": 1703984400,  # 2023-12-31 01:00:00 UTC
            "date": "2023-12-31 01:00:00",
        },
        {
            "track": "Between the Bars",
            "artist": "Elliott Smith",
            "album": "Either/Or",
            "timestamp": 1704067200,  # 2024-01-01 00:00:00 UTC
            "date": "2024-01-01 00:00:00",
        },
        {
            "track": "Say Yes",
            "artist": "Elliott Smith",
            "album": "Either/Or",
            "timestamp": 1704070800,  # 2024-01-01 01:00:00 UTC
            "date": "2024-01-01 01:00:00",
        },
        {
            "track": "Angeles",
            "artist": "Elliott Smith",
            "album": "Either/Or",
            "timestamp": 1704153600,  # 2024-01-02 00:00:00 UTC
            "date": "2024-01-02 00:00:00",
        },
    ]


@pytest.fixture
def sample_genre_cache():
    """Genre cache modeled after real genre_cache.json."""
    return {
        "stand atlantic": [
            "pop punk",
            "australian",
            "rock",
            "alternative rock",
            "female vocalists",
            "pop rock",
            "alternative",
            "punk",
            "australia",
            "2010s",
        ],
        "elliott smith": [
            "singer-songwriter",
            "folk",
            "indie",
            "acoustic",
            "indie rock",
            "indie folk",
            "lo-fi",
            "american",
            "indie pop",
            "alternative",
        ],
    }


@pytest.fixture
def sample_months(sample_scrobbles):
    """Pre-grouped month data (output of group_scrobbles_by_month)."""
    return [
        {
            "month": 12,
            "year": 2023,
            "tracks": sample_scrobbles[:2],
            "size": 2,
        },
        {
            "month": 1,
            "year": 2024,
            "tracks": sample_scrobbles[2:],
            "size": 3,
        },
    ]


@pytest.fixture
def analyzed_months(sample_months):
    """Month data enriched with genre/mood analysis (output of analyze_months)."""
    months = sample_months.copy()
    months[0]["genre_distribution"] = {"pop punk": 2, "rock": 2, "alternative rock": 2}
    months[0]["mood_distribution"] = {"angsty": 2}
    months[0]["primary_mood"] = "angsty"
    for track in months[0]["tracks"]:
        track["genres"] = [
            "pop punk",
            "australian",
            "rock",
            "alternative rock",
            "female vocalists",
            "pop rock",
            "alternative",
            "punk",
        ]
        track["mood"] = "angsty"

    months[1]["genre_distribution"] = {
        "singer-songwriter": 3,
        "folk": 3,
        "indie": 3,
    }
    months[1]["mood_distribution"] = {"introspective": 3}
    months[1]["primary_mood"] = "introspective"
    for track in months[1]["tracks"]:
        track["genres"] = [
            "singer-songwriter",
            "folk",
            "indie",
            "acoustic",
            "indie rock",
            "indie folk",
            "lo-fi",
            "american",
        ]
        track["mood"] = "introspective"

    return months


@pytest.fixture
def sample_api_track():
    """A single track as returned by the Last.fm API."""
    return {
        "name": "Satellite",
        "artist": {"name": "Stand Atlantic"},
        "album": {"#text": "Pink Elephant"},
        "date": {"uts": "1703980800", "#text": "31 Dec 2023, 00:00"},
    }


@pytest.fixture
def sample_api_track_nowplaying():
    """A currently-playing track from the Last.fm API (should be skipped)."""
    return {
        "name": "Currently Playing Song",
        "artist": {"name": "Some Artist"},
        "album": {"#text": "Some Album"},
        "@attr": {"nowplaying": "true"},
    }


@pytest.fixture
def sample_api_response():
    """A full API response page for user.getRecentTracks."""
    return {
        "recenttracks": {
            "@attr": {
                "page": "1",
                "totalPages": "1",
                "total": "2",
            },
            "track": [
                {
                    "name": "Satellite",
                    "artist": {"name": "Stand Atlantic"},
                    "album": {"#text": "Pink Elephant"},
                    "date": {"uts": "1703980800", "#text": "31 Dec 2023, 00:00"},
                },
                {
                    "name": "Between the Bars",
                    "artist": {"name": "Elliott Smith"},
                    "album": {"#text": "Either/Or"},
                    "date": {"uts": "1704067200", "#text": "01 Jan 2024, 00:00"},
                },
            ],
        }
    }


@pytest.fixture
def sample_genre_api_response():
    """API response for artist.gettoptags."""
    return {
        "toptags": {
            "tag": [
                {"name": "pop punk", "count": "100"},
                {"name": "rock", "count": "80"},
                {"name": "alternative", "count": "60"},
                {"name": "punk", "count": "50"},
                {"name": "australian", "count": "40"},
                {"name": "female vocalists", "count": "30"},
                {"name": "alternative rock", "count": "25"},
                {"name": "pop rock", "count": "20"},
                {"name": "punk rock", "count": "15"},
                {"name": "emo", "count": "10"},
            ]
        }
    }
