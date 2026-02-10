"""Tests for api.py - track parsing and API interaction (mocked)."""

from unittest.mock import MagicMock, patch

from scrobble_analysis.api import _parse_track, fetch_artist_genres, fetch_scrobbles


class TestParseTrack:
    def test_parses_valid_track(self, sample_api_track):
        result = _parse_track(sample_api_track)

        assert result is not None
        assert result["track"] == "Satellite"
        assert result["artist"] == "Stand Atlantic"
        assert result["album"] == "Pink Elephant"
        assert result["timestamp"] == 1703980800
        assert result["date"] == "2023-12-31 00:00:00"

    def test_skips_nowplaying_track(self, sample_api_track_nowplaying):
        result = _parse_track(sample_api_track_nowplaying)
        assert result is None

    def test_skips_track_with_zero_timestamp(self):
        track = {
            "name": "Some Track",
            "artist": {"name": "Some Artist"},
            "album": {"#text": "Some Album"},
            "date": {"uts": "0"},
        }
        result = _parse_track(track)
        assert result is None

    def test_skips_track_with_no_date(self):
        track = {
            "name": "Some Track",
            "artist": {"name": "Some Artist"},
            "album": {"#text": "Some Album"},
        }
        result = _parse_track(track)
        assert result is None

    def test_handles_string_artist(self):
        track = {
            "name": "Track",
            "artist": "String Artist",
            "album": {"#text": "Album"},
            "date": {"uts": "1703980800"},
        }
        result = _parse_track(track)

        assert result is not None
        assert result["artist"] == "String Artist"

    def test_handles_missing_album(self):
        track = {
            "name": "Track",
            "artist": {"name": "Artist"},
            "date": {"uts": "1703980800"},
        }
        result = _parse_track(track)

        assert result is not None
        assert result["album"] == ""

    def test_handles_empty_date_dict(self):
        track = {
            "name": "Track",
            "artist": {"name": "Artist"},
            "album": {"#text": "Album"},
            "date": {},
        }
        result = _parse_track(track)
        # uts defaults to 0, so should return None
        assert result is None


class TestFetchArtistGenres:
    @patch("scrobble_analysis.api._get_session")
    def test_returns_cached_genres(self, mock_session):
        cache = {"stand atlantic": ["pop punk", "rock"]}

        result = fetch_artist_genres("Stand Atlantic", "fake_key", cache)

        assert result == ["pop punk", "rock"]
        # Session is created at module level but no HTTP request should be made
        mock_session.return_value.get.assert_not_called()

    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_fetches_from_api_when_not_cached(
        self, mock_session, mock_sleep, sample_genre_api_response
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_genre_api_response
        mock_session.return_value.get.return_value = mock_response
        cache = {}

        result = fetch_artist_genres("Stand Atlantic", "fake_key", cache)

        assert len(result) == 10
        assert result[0] == "pop punk"
        assert "stand atlantic" in cache

    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_returns_empty_on_api_error(self, mock_session, mock_sleep):
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": 6, "message": "Artist not found"}
        mock_session.return_value.get.return_value = mock_response
        cache = {}

        result = fetch_artist_genres("Nonexistent Artist", "fake_key", cache, max_retries=1)

        assert result == []
        assert cache["nonexistent artist"] == []

    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_caches_empty_on_failure(self, mock_session, mock_sleep):
        mock_session.return_value.get.side_effect = Exception("Network error")
        cache = {}

        result = fetch_artist_genres("Artist", "fake_key", cache, max_retries=1)

        assert result == []
        assert cache["artist"] == []

    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_genre_tags_are_lowercased(self, mock_session, mock_sleep):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "toptags": {
                "tag": [
                    {"name": "Pop Punk", "count": "100"},
                    {"name": "ROCK", "count": "80"},
                ]
            }
        }
        mock_session.return_value.get.return_value = mock_response
        cache = {}

        result = fetch_artist_genres("Artist", "fake_key", cache)

        assert result == ["pop punk", "rock"]


class TestFetchScrobbles:
    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_fetches_single_page(
        self, mock_session, mock_sleep, mock_load, mock_save, sample_api_response
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_session.return_value.get.return_value = mock_response
        mock_load.return_value = {}

        result = fetch_scrobbles("testuser", "fake_key", use_cache=True)

        assert len(result) == 2
        assert result[0]["track"] == "Satellite"
        assert result[1]["track"] == "Between the Bars"

    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_returns_cached_when_complete_and_fresh(
        self, mock_session, mock_sleep, mock_load, mock_save
    ):
        import time

        mock_load.return_value = {
            "username": "testuser",
            "scrobbles": [{"track": "Cached Track", "timestamp": 123}],
            "last_fetch": time.time(),  # fresh
            "complete": True,
        }

        result = fetch_scrobbles("testuser", "fake_key", use_cache=True)

        assert len(result) == 1
        assert result[0]["track"] == "Cached Track"
        mock_session.return_value.get.assert_not_called()

    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_deduplicates_tracks(self, mock_session, mock_sleep, mock_load, mock_save):
        # Response with duplicate timestamps
        response = {
            "recenttracks": {
                "@attr": {"page": "1", "totalPages": "1", "total": "2"},
                "track": [
                    {
                        "name": "Same Track",
                        "artist": {"name": "Artist"},
                        "album": {"#text": "Album"},
                        "date": {"uts": "1703980800"},
                    },
                    {
                        "name": "Same Track Again",
                        "artist": {"name": "Artist"},
                        "album": {"#text": "Album"},
                        "date": {"uts": "1703980800"},  # same timestamp
                    },
                ],
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response
        mock_session.return_value.get.return_value = mock_response
        mock_load.return_value = {}

        result = fetch_scrobbles("testuser", "fake_key", use_cache=True)

        # Should deduplicate by timestamp
        assert len(result) == 1

    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_handles_single_track_dict_response(
        self, mock_session, mock_sleep, mock_load, mock_save
    ):
        # API sometimes returns a single track as a dict instead of a list
        response = {
            "recenttracks": {
                "@attr": {"page": "1", "totalPages": "1", "total": "1"},
                "track": {
                    "name": "Only Track",
                    "artist": {"name": "Solo Artist"},
                    "album": {"#text": "Solo Album"},
                    "date": {"uts": "1703980800"},
                },
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response
        mock_session.return_value.get.return_value = mock_response
        mock_load.return_value = {}

        result = fetch_scrobbles("testuser", "fake_key", use_cache=True)

        assert len(result) == 1
        assert result[0]["track"] == "Only Track"

    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_no_cache_mode(
        self, mock_session, mock_sleep, mock_load, mock_save, sample_api_response
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_session.return_value.get.return_value = mock_response

        result = fetch_scrobbles("testuser", "fake_key", use_cache=False)

        mock_load.assert_not_called()
        assert len(result) == 2

    @patch("scrobble_analysis.api.save_json_cache")
    @patch("scrobble_analysis.api.load_json_cache")
    @patch("scrobble_analysis.api.time.sleep")
    @patch("scrobble_analysis.api._get_session")
    def test_results_sorted_by_timestamp(
        self, mock_session, mock_sleep, mock_load, mock_save, sample_api_response
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_session.return_value.get.return_value = mock_response
        mock_load.return_value = {}

        result = fetch_scrobbles("testuser", "fake_key")

        timestamps = [s["timestamp"] for s in result]
        assert timestamps == sorted(timestamps)
