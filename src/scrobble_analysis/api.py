"""
Last.fm API interaction functions.
"""

import time
from datetime import datetime, timezone

import requests

from .cache import load_json_cache, save_json_cache
from .config import LASTFM_API_URL, SCROBBLE_CACHE_FILE

__all__ = ["fetch_scrobbles", "fetch_artist_genres"]

# Reusable session for connection pooling
_session: requests.Session | None = None


def _get_session() -> requests.Session:
    """Get or create a reusable requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": "ScrobbleAnalyzer/1.0"})
    return _session


def _parse_track(track: dict) -> dict | None:
    """Parse a track from API response into a scrobble dict."""
    # Skip currently playing tracks it's not a scrobble yet!
    if "@attr" in track and track["@attr"].get("nowplaying") == "true":
        return None

    date_info = track.get("date", {})
    timestamp = int(date_info.get("uts", 0)) if date_info else 0

    if timestamp == 0:
        return None

    # Handle artist field
    artist_data = track.get("artist", {})
    artist = artist_data.get("name", "") if isinstance(artist_data, dict) else artist_data

    # Handle album field
    album_data = track.get("album", {})
    album = album_data.get("#text", "") if isinstance(album_data, dict) else ""

    return {
        "track": track.get("name", ""),
        "artist": artist,
        "album": album,
        "timestamp": timestamp,
        "date": datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def fetch_scrobbles(
    username: str,
    api_key: str,
    from_date: datetime | None = None,
    use_cache: bool = True,
    max_retries: int = 5,
    base_delay: int = 10,
) -> list[dict]:
    """
    Fetch all scrobbles for a user from Last.fm API.

    Args:
        username: Last.fm username
        api_key: Last.fm API key
        from_date: Only fetch scrobbles after this date
        use_cache: Whether to use cached data
        max_retries: Maximum retry attempts on failure
        base_delay: Base delay in seconds for exponential backoff

    Returns:
        List of scrobble dictionaries
    """
    session = _get_session()
    cache = {}
    all_scrobbles: list[dict] = []
    page = 1
    total_pages = 1
    resuming = False

    if use_cache:
        cache = load_json_cache(SCROBBLE_CACHE_FILE)
        if cache.get("username") == username and cache.get("scrobbles"):
            # Check if complete cache < 1 hour old
            if cache.get("complete") and time.time() - cache.get("last_fetch", 0) < 3600:
                print(f"Using cached scrobbles ({len(cache['scrobbles'])} tracks)")
                cached_scrobbles: list[dict] = cache["scrobbles"]
                return cached_scrobbles

            # Check if incomplete fetch to resume
            if not cache.get("complete") and cache.get("scrobbles"):
                all_scrobbles = cache["scrobbles"]
                print(f"Resuming incomplete fetch ({len(all_scrobbles)} tracks already cached)")
                resuming = True

    print(f"Fetching scrobbles for user: {username}")

    consecutive_errors = 0
    seen_timestamps = {s["timestamp"] for s in all_scrobbles} if resuming else set()
    from_timestamp = int(from_date.timestamp()) if from_date else None

    while page <= total_pages:
        try:
            params: dict[str, str | int] = {
                "method": "user.getRecentTracks",
                "user": username,
                "api_key": api_key,
                "format": "json",
                "limit": 200,
                "page": page,
                "extended": 1,
            }
            if from_timestamp:
                params["from"] = from_timestamp

            response = session.get(LASTFM_API_URL, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                error_msg = data.get("message", "Unknown error")
                consecutive_errors += 1

                if consecutive_errors >= max_retries:
                    print(f"Max retries ({max_retries}) reached. Saving progress")
                    break

                delay = base_delay * (2 ** (consecutive_errors - 1))
                print(f"API Error: {error_msg}")
                print(f"Retry {consecutive_errors}/{max_retries} in {delay}s")
                time.sleep(delay)
                continue

            recent_tracks = data.get("recenttracks", {})
            total_pages = int(recent_tracks.get("@attr", {}).get("totalPages", 1))
            tracks = recent_tracks.get("track", [])

            if not tracks:
                break

            # Handle single track responses
            if isinstance(tracks, dict):
                tracks = [tracks]

            for track in tracks:
                scrobble = _parse_track(track)
                if scrobble and scrobble["timestamp"] not in seen_timestamps:
                    all_scrobbles.append(scrobble)
                    seen_timestamps.add(scrobble["timestamp"])

            # Success! reset error counter for sanity
            consecutive_errors = 0

            print(f"  Page {page}/{total_pages} - {len(all_scrobbles)} tracks fetched")
            page += 1
            time.sleep(0.25)  # Rate limiting i hate you

            # Save progress every 50 pages
            if page % 50 == 0:
                print("  Saving progress checkpoint")
                temp_cache = {
                    "username": username,
                    "scrobbles": sorted(all_scrobbles, key=lambda x: x["timestamp"]),
                    "last_fetch": time.time(),
                    "incomplete": True,
                    "last_page": page,
                    "total_pages": total_pages,
                }
                save_json_cache(temp_cache, SCROBBLE_CACHE_FILE)

        except requests.exceptions.Timeout:
            consecutive_errors += 1
            if consecutive_errors >= max_retries:
                print(f"  Max retries ({max_retries}) reached after timeouts. Saving progress")
                break

            delay = base_delay * (2 ** (consecutive_errors - 1))
            print(f"Request timeout on page {page}")
            print(f"Retry {consecutive_errors}/{max_retries} in {delay}s")
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            consecutive_errors += 1
            if consecutive_errors >= max_retries:
                print(f"Max retries ({max_retries}) reached. Saving progress")
                break

            delay = base_delay * (2 ** (consecutive_errors - 1))
            print(f"Network error on page {page}: {e}")
            print(f"Retry {consecutive_errors}/{max_retries} in {delay}s")
            time.sleep(delay)

        except Exception as e:
            consecutive_errors += 1
            if consecutive_errors >= max_retries:
                print(f"Max retries ({max_retries}) reached. Saving progress")
                break

            delay = base_delay * (2 ** (consecutive_errors - 1))
            print(f"Error fetching page {page}: {e}")
            print(f"Retry {consecutive_errors}/{max_retries} in {delay}s")
            time.sleep(delay)

    # Sort by timestamp (oldest first)
    all_scrobbles.sort(key=lambda x: x["timestamp"])

    # Cache the results
    is_complete = page > total_pages
    cache = {
        "username": username,
        "scrobbles": all_scrobbles,
        "last_fetch": time.time(),
        "complete": is_complete,
    }
    save_json_cache(cache, SCROBBLE_CACHE_FILE)

    status = "complete" if is_complete else f"partial ({page - 1}/{total_pages} pages)"
    print(f"Total scrobbles fetched: {len(all_scrobbles)} ({status})\n")
    return all_scrobbles


def fetch_artist_genres(
    artist_name: str,
    api_key: str,
    cache: dict,
    max_retries: int = 3,
    base_delay: int = 5,
) -> list[str]:
    """
    Fetch genre tags for an artist from Last.fm API.

    Args:
        artist_name: Name of the artist
        api_key: Last.fm API key
        cache: Dict to store/retrieve cached genres
        max_retries: Maximum retry attempts on failure
        base_delay: Base delay in seconds for exponential backoff

    Returns:
        List of genre tag strings
    """
    session = _get_session()
    cache_key = artist_name.lower()

    if cache_key in cache:
        cached_genres: list[str] = cache[cache_key]
        return cached_genres

    for attempt in range(max_retries):
        try:
            params = {
                "method": "artist.gettoptags",
                "artist": artist_name,
                "api_key": api_key,
                "format": "json",
            }
            response = session.get(LASTFM_API_URL, params=params, timeout=10)
            data = response.json()

            if "error" in data:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2**attempt))
                    continue
                break

            if "toptags" in data and "tag" in data["toptags"]:
                tags = [tag["name"].lower() for tag in data["toptags"]["tag"][:10]]
                cache[cache_key] = tags
                time.sleep(0.2)  # Rate limiting i hate you x2
                return tags
            break

        except (requests.exceptions.Timeout, requests.exceptions.RequestException):
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2**attempt))
                continue
            break

        except Exception as e:
            print(f"Warning: Could not fetch genres for '{artist_name}': {e}")
            break

    cache[cache_key] = []
    return []
