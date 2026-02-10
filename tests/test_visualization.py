"""Tests for visualization.py - GraphOptions, data preparation, and week grouping."""

from dataclasses import fields

from scrobble_analysis.visualization import GraphOptions, _group_tracks_by_week, _prepare_graph_data


class TestGraphOptions:
    def test_defaults_all_enabled_except_interactive(self):
        options = GraphOptions()

        for field in fields(options):
            if field.name == "month_detail":
                assert getattr(options, field.name) is False
            else:
                assert getattr(options, field.name) is True

    def test_all_enabled_classmethod(self):
        options = GraphOptions.all_enabled()

        assert options.activity is True
        assert options.dashboard is True
        assert options.month_detail is False
        assert options.any_enabled() is True

    def test_none_enabled_classmethod(self):
        options = GraphOptions.none_enabled()

        for field in fields(options):
            assert getattr(options, field.name) is False

        assert options.any_enabled() is False

    def test_any_enabled_with_one(self):
        options = GraphOptions.none_enabled()
        options.activity = True

        assert options.any_enabled() is True

    def test_any_enabled_with_none(self):
        options = GraphOptions.none_enabled()
        assert options.any_enabled() is False

    def test_individual_field_toggle(self):
        options = GraphOptions.all_enabled()
        options.dashboard = False

        assert options.activity is True
        assert options.dashboard is False
        assert options.any_enabled() is True

    def test_field_count(self):
        # 9 batch graph options + 1 interactive (month_detail)
        assert len(fields(GraphOptions)) == 10

    def test_month_detail_opt_in(self):
        options = GraphOptions.all_enabled()
        assert options.month_detail is False

        options.month_detail = True
        assert options.month_detail is True
        assert options.any_enabled() is True


class TestPrepareGraphData:
    def test_basic_structure(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert "dates" in data
        assert "sizes" in data
        assert "avg_size" in data
        assert "median_size" in data
        assert "std_size" in data
        assert "min_size" in data
        assert "max_size" in data
        assert "yearly_stats" in data
        assert "yearly_avgs" in data

    def test_dates_formatted(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert data["dates"] == ["Dec 2023", "Jan 2024"]

    def test_sizes_correct(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert data["sizes"] == [2, 3]
        assert data["min_size"] == 2
        assert data["max_size"] == 3

    def test_average_calculation(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert data["avg_size"] == 2.5

    def test_yearly_stats_grouped(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert 2023 in data["yearly_stats"]
        assert 2024 in data["yearly_stats"]
        assert data["yearly_stats"][2023] == [2]
        assert data["yearly_stats"][2024] == [3]

    def test_yearly_averages(self, analyzed_months):
        data = _prepare_graph_data(analyzed_months)

        assert data["yearly_avgs"][2023] == 2.0
        assert data["yearly_avgs"][2024] == 3.0


class TestGroupTracksByWeek:
    def test_groups_by_week_of_month(self, analyzed_months):
        # Dec 2023: 2 tracks on Dec 31 -> week 5 (day 31, idx = (31-1)//7 = 4)
        weeks = _group_tracks_by_week(analyzed_months[0])
        assert len(weeks) == 1
        assert weeks[0]["total"] == 2

    def test_jan_tracks_in_week_1(self, analyzed_months):
        # Jan 2024: 3 tracks on Jan 1-2 -> week 1 (days 1-2, idx = 0)
        weeks = _group_tracks_by_week(analyzed_months[1])
        assert len(weeks) == 1
        assert weeks[0]["total"] == 3

    def test_genre_aggregation(self, analyzed_months):
        weeks = _group_tracks_by_week(analyzed_months[1])
        assert "singer-songwriter" in weeks[0]["genre_counts"]

    def test_mood_aggregation(self, analyzed_months):
        weeks = _group_tracks_by_week(analyzed_months[1])
        assert "introspective" in weeks[0]["mood_counts"]
        assert weeks[0]["mood_counts"]["introspective"] == 3

    def test_empty_month(self):
        empty = {"year": 2024, "month": 6, "tracks": [], "size": 0}
        weeks = _group_tracks_by_week(empty)
        assert weeks == []

    def test_week_label_format(self, analyzed_months):
        weeks = _group_tracks_by_week(analyzed_months[1])
        assert weeks[0]["week_label"].startswith("Week")
        assert "Jan" in weeks[0]["week_label"]
