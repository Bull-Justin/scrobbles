"""Tests for visualization.py - GraphOptions and data preparation."""

from dataclasses import fields

from scrobble_analysis.visualization import GraphOptions, _prepare_graph_data


class TestGraphOptions:
    def test_defaults_all_enabled(self):
        options = GraphOptions()

        for field in fields(options):
            assert getattr(options, field.name) is True

    def test_all_enabled_classmethod(self):
        options = GraphOptions.all_enabled()

        assert options.activity is True
        assert options.dashboard is True
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
        # all 9 graph options
        assert len(fields(GraphOptions)) == 9


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
