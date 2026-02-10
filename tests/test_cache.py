"""Tests for cache.py - JSON cache load/save functionality."""

import json

from scrobble_analysis.cache import load_json_cache, save_json_cache


class TestLoadJsonCache:
    def test_load_existing_cache(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        data = {"artist_a": ["rock", "indie"], "artist_b": ["pop"]}
        cache_file.write_text(json.dumps(data), encoding="utf-8")

        result = load_json_cache(cache_file)

        assert result == data

    def test_load_nonexistent_file_returns_empty_dict(self, tmp_path):
        cache_file = tmp_path / "nonexistent.json"

        result = load_json_cache(cache_file)

        assert result == {}

    def test_load_empty_json_object(self, tmp_path):
        cache_file = tmp_path / "empty.json"
        cache_file.write_text("{}", encoding="utf-8")

        result = load_json_cache(cache_file)

        assert result == {}

    def test_load_preserves_nested_structure(self, tmp_path):
        cache_file = tmp_path / "nested.json"
        data = {
            "username": "Sir_Corndog",
            "scrobbles": [{"track": "Satellite", "artist": "Stand Atlantic"}],
            "last_fetch": 1703980800,
            "complete": True,
        }
        cache_file.write_text(json.dumps(data), encoding="utf-8")

        result = load_json_cache(cache_file)

        assert result["username"] == "Sir_Corndog"
        assert len(result["scrobbles"]) == 1
        assert result["complete"] is True


class TestSaveJsonCache:
    def test_save_creates_file(self, tmp_path):
        cache_file = tmp_path / "new_cache.json"
        data = {"artist": ["rock", "pop"]}

        save_json_cache(data, cache_file)

        assert cache_file.exists()
        loaded = json.loads(cache_file.read_text(encoding="utf-8"))
        assert loaded == data

    def test_save_overwrites_existing(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text('{"old": "data"}', encoding="utf-8")

        new_data = {"new": "data"}
        save_json_cache(new_data, cache_file)

        loaded = json.loads(cache_file.read_text(encoding="utf-8"))
        assert loaded == new_data
        assert "old" not in loaded

    def test_save_uses_indentation(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        save_json_cache({"key": "value"}, cache_file)

        content = cache_file.read_text(encoding="utf-8")
        assert "\n" in content  # indented JSON has newlines

    def test_roundtrip(self, tmp_path, sample_genre_cache):
        cache_file = tmp_path / "roundtrip.json"

        save_json_cache(sample_genre_cache, cache_file)
        result = load_json_cache(cache_file)

        assert result == sample_genre_cache
