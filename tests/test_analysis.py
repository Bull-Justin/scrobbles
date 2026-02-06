"""Tests for analysis.py - mood classification, grouping, and analysis."""

from unittest.mock import patch

from scrobble_analysis.analysis import (
    analyze_months,
    classify_mood,
    group_scrobbles_by_month,
)


class TestClassifyMood:
    def test_angsty_genres(self):
        genres = ("emo", "pop punk", "screamo")
        assert classify_mood(genres) == "angsty"

    def test_introspective_genres(self):
        genres = ("singer-songwriter", "folk", "acoustic")
        assert classify_mood(genres) == "introspective"

    def test_dreamy_genres(self):
        genres = ("shoegaze", "dream pop", "ambient")
        assert classify_mood(genres) == "dreamy"

    def test_aggressive_genres(self):
        genres = ("death metal", "black metal", "grindcore")
        assert classify_mood(genres) == "aggressive"

    def test_danceable_genres(self):
        genres = ("pop", "dance", "disco")
        assert classify_mood(genres) == "danceable"

    def test_melancholic_genres(self):
        genres = ("slowcore", "sadcore", "gothic")
        assert classify_mood(genres) == "melancholic"

    def test_chaotic_genres(self):
        genres = ("math rock", "noise", "experimental")
        assert classify_mood(genres) == "chaotic"

    def test_nostalgic_genres(self):
        genres = ("80s", "classic rock", "retro")
        assert classify_mood(genres) == "nostalgic"

    def test_warm_genres(self):
        genres = ("lo-fi", "bedroom pop", "mellow")
        assert classify_mood(genres) == "warm"

    def test_energetic_genres(self):
        genres = ("rock", "indie rock", "garage rock")
        assert classify_mood(genres) == "energetic"

    def test_no_matching_genres_returns_neutral(self):
        genres = ("field recording", "musique concrete", "plunderphonics")
        assert classify_mood(genres) == "neutral"

    def test_empty_genres_returns_neutral(self):
        assert classify_mood(()) == "neutral"

    def test_mixed_genres_returns_highest_scoring(self):
        # 2 angsty (emo, pop punk) vs 1 energetic (rock)
        genres = ("emo", "pop punk", "rock")
        assert classify_mood(genres) == "angsty"

    def test_substring_matching(self):
        # "post-hardcore" is an exact match in MOOD_MAPPINGS for angsty
        genres = ("post-hardcore",)
        assert classify_mood(genres) == "angsty"

    def test_case_insensitive(self):
        genres = ("EMO", "POP PUNK")
        # genre_lower comparison should handle uppercase
        result = classify_mood(genres)
        # "EMO".lower() == "emo" which is in _KEYWORD_TO_MOOD
        assert result == "angsty"


class TestGroupScrobblesByMonth:
    def test_groups_by_month(self, sample_scrobbles):
        result = group_scrobbles_by_month(sample_scrobbles)

        assert len(result) == 2
        assert result[0]["year"] == 2023
        assert result[0]["month"] == 12
        assert result[0]["size"] == 2
        assert result[1]["year"] == 2024
        assert result[1]["month"] == 1
        assert result[1]["size"] == 3

    def test_sorted_chronologically(self, sample_scrobbles):
        # Reverse the input to test sorting
        reversed_scrobbles = list(reversed(sample_scrobbles))
        result = group_scrobbles_by_month(reversed_scrobbles)

        assert result[0]["year"] == 2023
        assert result[1]["year"] == 2024

    def test_empty_input(self):
        result = group_scrobbles_by_month([])
        assert result == []

    def test_single_scrobble(self):
        scrobbles = [
            {
                "track": "Test",
                "artist": "Test Artist",
                "album": "Test Album",
                "timestamp": 1704067200,  # 2024-01-01
                "date": "2024-01-01 00:00:00",
            }
        ]

        result = group_scrobbles_by_month(scrobbles)

        assert len(result) == 1
        assert result[0]["size"] == 1
        assert result[0]["month"] == 1
        assert result[0]["year"] == 2024

    def test_tracks_preserved_in_group(self, sample_scrobbles):
        result = group_scrobbles_by_month(sample_scrobbles)

        # December 2023 should have the Stand Atlantic tracks
        dec_tracks = result[0]["tracks"]
        assert all(t["artist"] == "Stand Atlantic" for t in dec_tracks)


class TestAnalyzeMonths:
    @patch("scrobble_analysis.analysis.save_json_cache")
    @patch("scrobble_analysis.analysis.load_json_cache")
    @patch("scrobble_analysis.analysis.fetch_artist_genres")
    def test_enriches_months_with_genre_data(
        self, mock_fetch, mock_load, mock_save, sample_months, sample_genre_cache
    ):
        mock_load.return_value = sample_genre_cache

        result = analyze_months(sample_months, "fake_api_key")

        # All artists already cached, so fetch shouldn't be called
        mock_fetch.assert_not_called()
        # No uncached artists, so save shouldn't be called
        mock_save.assert_not_called()

        # Check enrichment
        for month in result:
            assert "genre_distribution" in month
            assert "mood_distribution" in month
            assert "primary_mood" in month

    @patch("scrobble_analysis.analysis.save_json_cache")
    @patch("scrobble_analysis.analysis.load_json_cache")
    @patch("scrobble_analysis.analysis.fetch_artist_genres")
    def test_fetches_uncached_artists(self, mock_fetch, mock_load, mock_save, sample_months):
        # Empty cache - all artists need fetching
        mock_load.return_value = {}

        analyze_months(sample_months, "fake_api_key")

        # Should fetch for both unique artists
        assert mock_fetch.call_count == 2
        mock_save.assert_called_once()

    @patch("scrobble_analysis.analysis.save_json_cache")
    @patch("scrobble_analysis.analysis.load_json_cache")
    @patch("scrobble_analysis.analysis.fetch_artist_genres")
    def test_mood_classification_applied(
        self, mock_fetch, mock_load, mock_save, sample_months, sample_genre_cache
    ):
        mock_load.return_value = sample_genre_cache

        result = analyze_months(sample_months, "fake_api_key")

        # Stand Atlantic genres include rock, alternative rock, punk -> energetic wins
        assert result[0]["primary_mood"] == "energetic"
        # Elliott Smith -> singer-songwriter, folk, acoustic -> introspective
        assert result[1]["primary_mood"] == "introspective"

    @patch("scrobble_analysis.analysis.save_json_cache")
    @patch("scrobble_analysis.analysis.load_json_cache")
    @patch("scrobble_analysis.analysis.fetch_artist_genres")
    def test_genre_distribution_top_10(
        self, mock_fetch, mock_load, mock_save, sample_months, sample_genre_cache
    ):
        mock_load.return_value = sample_genre_cache

        result = analyze_months(sample_months, "fake_api_key")

        # Each month should have at most 10 genres in distribution
        for month in result:
            assert len(month["genre_distribution"]) <= 10

    @patch("scrobble_analysis.analysis.save_json_cache")
    @patch("scrobble_analysis.analysis.load_json_cache")
    @patch("scrobble_analysis.analysis.fetch_artist_genres")
    def test_tracks_get_genres_and_mood_attached(
        self, mock_fetch, mock_load, mock_save, sample_months, sample_genre_cache
    ):
        mock_load.return_value = sample_genre_cache

        result = analyze_months(sample_months, "fake_api_key")

        for month in result:
            for track in month["tracks"]:
                assert "genres" in track
                assert "mood" in track
