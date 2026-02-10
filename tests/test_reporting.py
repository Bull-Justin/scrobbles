"""Tests for reporting.py - report generation and CSV export."""

import csv

from scrobble_analysis.reporting import (
    _collect_track_stats,
    export_to_csv,
    generate_report,
)


class TestCollectTrackStats:
    def test_collects_unique_artists(self, analyzed_months):
        artists, tracks = _collect_track_stats(analyzed_months)

        assert "Stand Atlantic" in artists
        assert "Elliott Smith" in artists
        assert len(artists) == 2

    def test_collects_unique_tracks(self, analyzed_months):
        artists, tracks = _collect_track_stats(analyzed_months)

        assert ("Stand Atlantic", "Satellite") in tracks
        assert ("Elliott Smith", "Between the Bars") in tracks

    def test_empty_months(self):
        artists, tracks = _collect_track_stats([])
        assert len(artists) == 0
        assert len(tracks) == 0


class TestGenerateReport:
    def test_returns_months(self, analyzed_months):
        result = generate_report(analyzed_months)
        assert result is analyzed_months

    def test_prints_summary(self, analyzed_months, capsys):
        generate_report(analyzed_months)
        captured = capsys.readouterr()

        assert "Total scrobbles: 5" in captured.out
        assert "Unique artists: 2" in captured.out
        assert "Total months analyzed: 2" in captured.out

    def test_prints_yearly_analysis(self, analyzed_months, capsys):
        generate_report(analyzed_months)
        captured = capsys.readouterr()

        assert "2023:" in captured.out
        assert "2024:" in captured.out

    def test_prints_monthly_breakdown(self, analyzed_months, capsys):
        generate_report(analyzed_months)
        captured = capsys.readouterr()

        assert "December:" in captured.out or "January:" in captured.out

    def test_prints_top_artists(self, analyzed_months, capsys):
        generate_report(analyzed_months)
        captured = capsys.readouterr()

        assert "Elliott Smith" in captured.out
        assert "Stand Atlantic" in captured.out


class TestExportToCsv:
    def test_creates_monthly_csv(self, analyzed_months, tmp_path, monkeypatch):
        monkeypatch.setattr("scrobble_analysis.reporting.OUTPUT_DIR", tmp_path)

        export_to_csv(analyzed_months)

        csv_path = tmp_path / "monthly_analysis.csv"
        assert csv_path.exists()

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Header + 2 months
        assert len(rows) == 3
        assert rows[0] == [
            "Year",
            "Month",
            "Scrobbles",
            "Primary Mood",
            "Top Genres",
            "Mood Distribution",
        ]

    def test_creates_detailed_scrobbles_csv(self, analyzed_months, tmp_path, monkeypatch):
        monkeypatch.setattr("scrobble_analysis.reporting.OUTPUT_DIR", tmp_path)

        export_to_csv(analyzed_months)

        detailed_path = tmp_path / "all_scrobbles.csv"
        assert detailed_path.exists()

        with open(detailed_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Header + 5 scrobbles
        assert len(rows) == 6
        assert rows[0] == ["Date", "Artist", "Track", "Album", "Mood", "Genres"]

    def test_custom_output_filename(self, analyzed_months, tmp_path, monkeypatch):
        monkeypatch.setattr("scrobble_analysis.reporting.OUTPUT_DIR", tmp_path)

        export_to_csv(analyzed_months, output_file="custom_name.csv")

        assert (tmp_path / "custom_name.csv").exists()

    def test_csv_content_accuracy(self, analyzed_months, tmp_path, monkeypatch):
        monkeypatch.setattr("scrobble_analysis.reporting.OUTPUT_DIR", tmp_path)

        export_to_csv(analyzed_months)

        csv_path = tmp_path / "monthly_analysis.csv"
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check December 2023 row
        dec_row = rows[1]
        assert dec_row[0] == "2023"  # Year
        assert dec_row[1] == "12"  # Month
        assert dec_row[2] == "2"  # Scrobbles
        assert dec_row[3] == "angsty"  # Primary Mood

    def test_detailed_csv_content(self, analyzed_months, tmp_path, monkeypatch):
        monkeypatch.setattr("scrobble_analysis.reporting.OUTPUT_DIR", tmp_path)

        export_to_csv(analyzed_months)

        detailed_path = tmp_path / "all_scrobbles.csv"
        with open(detailed_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # First data row should be a Stand Atlantic track
        first_track = rows[1]
        assert first_track[1] == "Stand Atlantic"  # Artist
        assert first_track[4] == "angsty"  # Mood
