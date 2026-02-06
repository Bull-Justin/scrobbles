"""Tests for cli.py - argument parsing, date handling, and graph options."""

from datetime import timezone

import pytest

from scrobble_analysis.cli import parse_date, parse_graph_options


class TestParseDate:
    def test_valid_date(self):
        result = parse_date("2024-01-15")

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.tzinfo == timezone.utc

    def test_empty_string_returns_none(self):
        assert parse_date("") is None

    def test_none_returns_none(self):
        assert parse_date(None) is None

    def test_invalid_format_exits(self):
        with pytest.raises(SystemExit):
            parse_date("not-a-date")

    def test_wrong_format_exits(self):
        with pytest.raises(SystemExit):
            parse_date("01/15/2024")


class TestParseGraphOptions:
    def _make_args(self, no_graphs=False, graphs=None):
        """Helper to create a mock args namespace."""
        from argparse import Namespace

        return Namespace(no_graphs=no_graphs, graphs=graphs)

    def test_no_graphs_disables_all(self):
        args = self._make_args(no_graphs=True)
        result = parse_graph_options(args)

        assert not result.activity
        assert not result.dashboard
        assert not result.any_enabled()

    def test_default_enables_all(self):
        args = self._make_args()
        result = parse_graph_options(args)

        assert result.activity
        assert result.mood_trends
        assert result.genres_by_year
        assert result.genres_overall
        assert result.mood_timeline
        assert result.top_artists
        assert result.day_of_week
        assert result.hour_of_day
        assert result.dashboard

    def test_specific_graphs_selection(self):
        args = self._make_args(graphs="activity,dashboard")
        result = parse_graph_options(args)

        assert result.activity is True
        assert result.dashboard is True
        assert result.mood_trends is False
        assert result.top_artists is False

    def test_single_graph_selection(self):
        args = self._make_args(graphs="top_artists")
        result = parse_graph_options(args)

        assert result.top_artists is True
        assert result.activity is False

    def test_unknown_graph_type_ignored(self, capsys):
        args = self._make_args(graphs="activity,nonexistent")
        result = parse_graph_options(args)

        assert result.activity is True
        captured = capsys.readouterr()
        assert "Unknown graph type 'nonexistent'" in captured.out

    def test_all_graph_types(self):
        all_graphs = (
            "activity,mood_trends,genres_by_year,genres_overall,"
            "mood_timeline,top_artists,day_of_week,hour_of_day,dashboard"
        )
        args = self._make_args(graphs=all_graphs)
        result = parse_graph_options(args)

        assert result.activity
        assert result.mood_trends
        assert result.genres_by_year
        assert result.genres_overall
        assert result.mood_timeline
        assert result.top_artists
        assert result.day_of_week
        assert result.hour_of_day
        assert result.dashboard
