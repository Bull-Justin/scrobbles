"""
Visualization functions for generating analysis graphs.
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from .config import MOOD_COLORS, OUTPUT_DIR

__all__ = ["GraphOptions", "generate_graphs"]


def _get_colormap(name: str, n: int) -> NDArray[np.floating[Any]]:
    """Get colors from a named colormap."""
    cmap = matplotlib.colormaps[name]
    return np.array(cmap(np.linspace(0, 1, n)))

# Short month names for graph labels
MONTH_NAMES: tuple[str, ...] = (
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
)


@dataclass
class GraphOptions:
    """Options for which graphs to generate."""
    activity: bool = True
    mood_trends: bool = True
    genres_by_year: bool = True
    genres_overall: bool = True
    mood_timeline: bool = True
    top_artists: bool = True
    day_of_week: bool = True
    hour_of_day: bool = True
    dashboard: bool = True

    @classmethod
    def all_enabled(cls) -> "GraphOptions":
        """Create options with all graphs enabled."""
        return cls()

    @classmethod
    def none_enabled(cls) -> "GraphOptions":
        """Create options with all graphs disabled."""
        return cls(**{f.name: False for f in fields(cls)})

    def any_enabled(self) -> bool:
        """Check if any graph option is enabled."""
        return any(getattr(self, f.name) for f in fields(self))


def _prepare_graph_data(months: list[dict]) -> dict[str, Any]:
    """Prepare common data for graph generation"""
    dates = [f"{MONTH_NAMES[m['month']]} {m['year']}" for m in months]
    sizes = [m["size"] for m in months]

    yearly_stats: dict[int, list[int]] = defaultdict(list)
    for m in months:
        yearly_stats[m["year"]].append(m["size"])

    sizes_array = np.array(sizes)

    return {
        "dates": dates,
        "sizes": sizes,
        "avg_size": float(np.mean(sizes_array)),
        "median_size": float(np.median(sizes_array)),
        "std_size": float(np.std(sizes_array)),
        "min_size": min(sizes),
        "max_size": max(sizes),
        "yearly_stats": dict(yearly_stats),
        "yearly_avgs": {year: float(np.mean(vals)) for year, vals in yearly_stats.items()}
    }

# I actually forget the best way to structure this but whatever, I haven't done this in 2 years. Some of the numbers are just vibes as well
def _save_figure(graphs_dir: Path, filename: str) -> None:
    """Save current figure and close it"""
    plt.tight_layout()
    plt.savefig(graphs_dir / filename, dpi=150)
    plt.close()
    print(f"  Saved: {filename}")


def generate_activity_graph(months: list[dict], graphs_dir: Path, data: dict) -> None:
    """Generate scrobble activity trends graph"""
    fig, ax = plt.subplots(figsize=(14, 6))

    colors = [MOOD_COLORS.get(m.get("primary_mood", "neutral"), "#95a5a6") for m in months]
    ax.bar(range(len(data["dates"])), data["sizes"], color=colors, edgecolor="white", linewidth=0.5)

    ax.set_xticks(range(len(data["dates"])))
    ax.set_xticklabels(data["dates"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Number of Scrobbles")
    ax.set_title("Monthly Scrobbles (colored by primary mood)")
    ax.set_ylim(0, data["max_size"] * 1.15)

    ax.axhline(y=data["avg_size"], color="#e74c3c", linestyle="--", linewidth=2,
               label=f"Overall Avg: {data['avg_size']:.1f}")

    # Add yearly average segments
    idx = 0
    for year in sorted(data["yearly_stats"].keys()):
        year_count = len(data["yearly_stats"][year])
        year_avg = data["yearly_avgs"][year]
        ax.hlines(y=year_avg, xmin=idx - 0.4, xmax=idx + year_count - 0.6,
                  color="#2c3e50", linestyle="-", linewidth=2.5, alpha=0.8)
        ax.text(idx + year_count / 2 - 0.5, year_avg + data["max_size"] * 0.03,
                f"{year}: {year_avg:.1f}", ha="center", fontsize=9, fontweight="bold", color="#2c3e50")
        idx += year_count

    stats_text = (
        f"Overall Stats:\n  Mean: {data['avg_size']:.1f}\n  Median: {data['median_size']:.1f}\n"
        f"  Std Dev: {data['std_size']:.1f}\n  Min: {data['min_size']}\n  Max: {data['max_size']}"
    )
    props = {"boxstyle": "round,pad=0.5", "facecolor": "white", "alpha": 0.9, "edgecolor": "#bdc3c7"}
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment="top", bbox=props, family="monospace")

    legend_patches = [
        mpatches.Patch(color=color, label=mood.capitalize())
        for mood, color in MOOD_COLORS.items() if mood != "neutral"
    ]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=8)

    _save_figure(graphs_dir, "scrobble_activity.png")


def generate_mood_trends_graph(months: list[dict], graphs_dir: Path, data: dict) -> None:
    """Generate mood distribution over time graph"""
    all_moods = list(MOOD_COLORS.keys())
    mood_data: dict[str, list[float]] = {mood: [] for mood in all_moods}

    for m in months:
        mood_dist = m.get("mood_distribution", {})
        total = sum(mood_dist.values()) or 1
        for mood in all_moods:
            mood_data[mood].append(mood_dist.get(mood, 0) / total * 100)

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(months))

    for mood in all_moods:
        values = mood_data[mood]
        ax.bar(range(len(data["dates"])), values, bottom=bottom, label=mood.capitalize(),
               color=MOOD_COLORS[mood], edgecolor="white", linewidth=0.3)
        bottom += np.array(values)

    ax.set_xticks(range(len(data["dates"])))
    ax.set_xticklabels(data["dates"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Percentage of Scrobbles")
    ax.set_title("Mood Distribution Over Time")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=8)

    _save_figure(graphs_dir, "mood_trends.png")


def generate_genres_by_year_graph(months: list[dict], graphs_dir: Path) -> None:
    """Generate genre distribution by year graph."""
    yearly_genres: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for m in months:
        year = m["year"]
        for genre, count in m.get("genre_distribution", {}).items():
            yearly_genres[year][genre] += count

    years = sorted(yearly_genres.keys())
    if not years:
        return

    fig, axes = plt.subplots(1, len(years), figsize=(5 * len(years), 6))
    if len(years) == 1:
        axes = [axes]

    genre_colors = _get_colormap("Set3", 12)

    for ax, year in zip(axes, years, strict=True):
        genres = yearly_genres[year]
        top_genres = sorted(genres.items(), key=lambda x: -x[1])[:10]
        if top_genres:
            names, counts = zip(*top_genres, strict=True)
            y_pos = np.arange(len(names))
            ax.barh(y_pos, counts, color=genre_colors[:len(names)])
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel("Scrobble Count")
            ax.set_title(f"Top Genres - {year}")

    _save_figure(graphs_dir, "genres_by_year.png")


def generate_genres_overall_graph(months: list[dict], graphs_dir: Path) -> None:
    """Generate overall genre distribution pie chart."""
    all_genres: dict[str, int] = defaultdict(int)
    for m in months:
        for genre, count in m.get("genre_distribution", {}).items():
            all_genres[genre] += count

    top_genres = sorted(all_genres.items(), key=lambda x: -x[1])[:10]
    if not top_genres:
        return

    other_count = sum(count for _, count in sorted(all_genres.items(), key=lambda x: -x[1])[10:])
    genre_names, genre_counts = zip(*top_genres, strict=True)
    all_names = list(genre_names) + ["other"]
    all_counts = list(genre_counts) + [other_count]

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = _get_colormap("Paired", len(all_names)).tolist()
    ax.pie(all_counts, labels=all_names, autopct="%1.1f%%", colors=colors, pctdistance=0.8)
    ax.set_title("Overall Genre Distribution")

    _save_figure(graphs_dir, "genres_overall.png")


def generate_mood_timeline_graph(months: list[dict], graphs_dir: Path, data: dict) -> None:
    """Generate mood timeline graph."""
    fig, ax = plt.subplots(figsize=(14, 3))

    for i, m in enumerate(months):
        mood = m.get("primary_mood", "neutral")
        color = MOOD_COLORS.get(mood, "#95a5a6")
        ax.add_patch(plt.Rectangle((i, 0), 0.9, 1, color=color))
        ax.text(i + 0.45, 0.5, mood[:3], ha="center", va="center",
                fontsize=7, color="white", fontweight="bold")

    ax.set_xlim(0, len(months))
    ax.set_ylim(0, 1)
    ax.set_xticks([i + 0.45 for i in range(len(months))])
    ax.set_xticklabels(data["dates"], rotation=45, ha="right", fontsize=8)
    ax.set_yticks([])
    ax.set_title("Primary Mood Timeline")

    legend_patches = [
        mpatches.Patch(color=color, label=mood.capitalize())
        for mood, color in MOOD_COLORS.items()
    ]
    ax.legend(handles=legend_patches, loc="upper left", bbox_to_anchor=(1, 1), fontsize=8)

    _save_figure(graphs_dir, "mood_timeline.png")


def generate_top_artists_graph(months: list[dict], graphs_dir: Path) -> None:
    """Generate top artists bar chart."""
    artist_counts: dict[str, int] = defaultdict(int)
    for m in months:
        for t in m["tracks"]:
            artist_counts[t["artist"]] += 1

    top_artists = sorted(artist_counts.items(), key=lambda x: -x[1])[:15]
    if not top_artists:
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    artists, counts = zip(*top_artists, strict=True)
    y_pos = np.arange(len(artists))
    colors = _get_colormap("viridis", len(artists))

    bars = ax.barh(y_pos, counts, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(artists, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Scrobble Count")
    ax.set_title("Top 15 Artists by Scrobble Count")

    max_count = max(counts)
    for bar, count in zip(bars, counts, strict=True):
        ax.text(bar.get_width() + max_count * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{count}", va="center", fontsize=9)

    _save_figure(graphs_dir, "top_artists.png")


def generate_day_of_week_graph(months: list[dict], graphs_dir: Path) -> None:
    """Generate listening by day of week graph."""
    day_counts: dict[int, int] = defaultdict(int)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for m in months:
        for t in m["tracks"]:
            dt = datetime.fromtimestamp(t["timestamp"], tz=timezone.utc)
            day_counts[dt.weekday()] += 1

    fig, ax = plt.subplots(figsize=(10, 6))
    days = list(range(7))
    counts = [day_counts[d] for d in days]
    colors = _get_colormap("Blues", 7)

    bars = ax.bar(days, counts, color=colors, edgecolor="white")
    ax.set_xticks(days)
    ax.set_xticklabels(day_names, rotation=45, ha="right")
    ax.set_ylabel("Total Scrobbles")
    ax.set_title("Listening Activity by Day of Week")

    max_count = max(counts)
    for bar, count in zip(bars, counts, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_count * 0.01,
                f"{count}", ha="center", fontsize=9)

    _save_figure(graphs_dir, "day_of_week.png")


def generate_hour_of_day_graph(months: list[dict], graphs_dir: Path) -> None:
    """Generate listening by hour of day graph."""
    hour_counts: dict[int, int] = defaultdict(int)

    for m in months:
        for t in m["tracks"]:
            dt = datetime.fromtimestamp(t["timestamp"], tz=timezone.utc)
            hour_counts[dt.hour] += 1

    fig, ax = plt.subplots(figsize=(12, 6))
    hours = list(range(24))
    counts = [hour_counts[h] for h in hours]
    colors = _get_colormap("plasma", 24)

    ax.bar(hours, counts, color=colors, edgecolor="white", width=0.8)
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h:02d}" for h in hours])
    ax.set_xlabel("Hour of Day (UTC)")
    ax.set_ylabel("Total Scrobbles")
    ax.set_title("Listening Activity by Hour of Day")

    _save_figure(graphs_dir, "hour_of_day.png")


def generate_dashboard(months: list[dict], graphs_dir: Path, data: dict) -> None:
    """Generate summary dashboard."""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

    # Overall stats panel
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis("off")
    ax1.set_title("Overall Statistics", fontsize=14, fontweight="bold", loc="left")

    total_scrobbles = sum(data["sizes"])
    unique_artists = len({t["artist"] for m in months for t in m["tracks"]})
    unique_tracks = len({(t["artist"], t["track"]) for m in months for t in m["tracks"]})

    stats_lines = [
        f"Total Months: {len(months)}",
        f"Total Scrobbles: {total_scrobbles}",
        f"Unique Artists: {unique_artists}",
        f"Unique Tracks: {unique_tracks}",
        "",
        f"Avg Scrobbles/Month: {data['avg_size']:.1f}",
        f"Median: {data['median_size']:.1f}",
        f"Std Deviation: {data['std_size']:.1f}",
        f"Min/Max: {data['min_size']} / {data['max_size']}",
    ]
    ax1.text(0.05, 0.9, "\n".join(stats_lines), transform=ax1.transAxes,
             fontsize=11, verticalalignment="top", family="monospace",
             bbox={"boxstyle": "round,pad=0.5", "facecolor": "#ecf0f1", "edgecolor": "#bdc3c7"})

    # Yearly summary table
    ax2 = fig.add_subplot(gs[0, 1:])
    ax2.axis("off")
    ax2.set_title("Yearly Summary", fontsize=14, fontweight="bold", loc="left")

    yearly_summary = []
    for year in sorted(data["yearly_stats"].keys()):
        year_sizes = data["yearly_stats"][year]
        year_moods: dict[str, int] = defaultdict(int)
        for m in months:
            if m["year"] == year:
                for mood, count in m.get("mood_distribution", {}).items():
                    year_moods[mood] += count
        top_mood = max(year_moods, key=lambda k: year_moods[k]) if year_moods else "N/A"

        yearly_summary.append({
            "year": year,
            "months": len(year_sizes),
            "total": sum(year_sizes),
            "avg": np.mean(year_sizes),
            "min": min(year_sizes),
            "max": max(year_sizes),
            "top_mood": top_mood
        })

    table_data = [["Year", "Months", "Total", "Avg", "Min", "Max", "Top Mood"]]
    for ys in yearly_summary:
        table_data.append([
            str(ys["year"]),
            str(ys["months"]),
            str(ys["total"]),
            f"{ys['avg']:.1f}",
            str(ys["min"]),
            str(ys["max"]),
            ys["top_mood"].capitalize()
        ])

    table = ax2.table(cellText=table_data, loc="center", cellLoc="center",
                      colWidths=[0.12, 0.12, 0.12, 0.12, 0.1, 0.1, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    for j in range(len(table_data[0])):
        table[(0, j)].set_facecolor("#3498db")
        table[(0, j)].set_text_props(color="white", fontweight="bold")

    for i in range(1, len(table_data)):
        for j in range(len(table_data[0])):
            if i % 2 == 0:
                table[(i, j)].set_facecolor("#ecf0f1")

    # Mood distribution pie
    ax3 = fig.add_subplot(gs[1, 0])
    overall_moods: dict[str, int] = defaultdict(int)
    for m in months:
        for mood, count in m.get("mood_distribution", {}).items():
            overall_moods[mood] += count

    if overall_moods:
        sorted_moods = sorted(overall_moods.items(), key=lambda x: -x[1])
        mood_names, mood_counts = zip(*sorted_moods, strict=True)
        mood_colors_list = [MOOD_COLORS.get(m, "#95a5a6") for m in mood_names]
        pie_result = ax3.pie(mood_counts, labels=None, autopct="%1.1f%%",
                             colors=mood_colors_list, pctdistance=0.75)
        wedges = pie_result[0]
        ax3.set_title("Overall Mood Distribution", fontsize=12, fontweight="bold")
        ax3.legend(wedges, [m.capitalize() for m in mood_names],
                   loc="center left", bbox_to_anchor=(-0.3, 0.5), fontsize=8)

    # Scrobble distribution histogram
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.hist(data["sizes"], bins=10, color="#3498db", edgecolor="white", alpha=0.8)
    ax4.axvline(x=data["avg_size"], color="#e74c3c", linestyle="--", linewidth=2,
                label=f"Mean: {data['avg_size']:.1f}")
    ax4.axvline(x=data["median_size"], color="#2ecc71", linestyle="--", linewidth=2,
                label=f"Median: {data['median_size']:.1f}")
    ax4.set_xlabel("Monthly Scrobbles")
    ax4.set_ylabel("Frequency")
    ax4.set_title("Scrobble Distribution", fontsize=12, fontweight="bold")
    ax4.legend(fontsize=9)

    # Trend line
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.plot(range(len(data["sizes"])), data["sizes"], marker="o", color="#3498db",
             linewidth=2, markersize=4)
    ax5.axhline(y=data["avg_size"], color="#e74c3c", linestyle="--", linewidth=1.5, alpha=0.7)
    ax5.fill_between(range(len(data["sizes"])),
                     data["avg_size"] - data["std_size"],
                     data["avg_size"] + data["std_size"],
                     alpha=0.2, color="#e74c3c", label=f"+/- 1 Std Dev ({data['std_size']:.1f})")
    ax5.set_xlabel("Month Index")
    ax5.set_ylabel("Scrobbles")
    ax5.set_title("Activity Trend with Variability", fontsize=12, fontweight="bold")
    ax5.legend(fontsize=8)

    # Year-over-year comparison
    ax6 = fig.add_subplot(gs[2, :])
    years = sorted(data["yearly_stats"].keys())
    x_positions = np.arange(len(years))
    width = 0.35

    year_totals = [sum(data["yearly_stats"][y]) for y in years]
    year_avgs = [np.mean(data["yearly_stats"][y]) for y in years]

    bars1 = ax6.bar(x_positions - width / 2, year_totals, width, label="Total Scrobbles", color="#3498db")
    ax6_twin = ax6.twinx()
    bars2 = ax6_twin.bar(x_positions + width / 2, year_avgs, width, label="Avg/Month", color="#2ecc71")

    ax6.set_xlabel("Year")
    ax6.set_ylabel("Total Scrobbles", color="#3498db")
    ax6_twin.set_ylabel("Average per Month", color="#2ecc71")
    ax6.set_xticks(x_positions)
    ax6.set_xticklabels(years)
    ax6.set_title("Year-over-Year: Total Scrobbles vs Average per Month", fontsize=12, fontweight="bold")

    for bar in bars1:
        height = bar.get_height()
        ax6.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax6_twin.annotate(f"{height:.1f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                          xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)

    lines1, labels1 = ax6.get_legend_handles_labels()
    lines2, labels2 = ax6_twin.get_legend_handles_labels()
    ax6.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.suptitle("Last.fm Scrobble Analysis - Summary Dashboard", fontsize=16, fontweight="bold", y=0.98)
    plt.savefig(graphs_dir / "summary_dashboard.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved: summary_dashboard.png")


def generate_graphs(months: list[dict], options: GraphOptions | None = None) -> None:
    """
    Generate all visualizations based on options.

    Args:
        months: List of month dictionaries with analysis data
        options: GraphOptions to control which graphs to generate
    """
    if options is None:
        options = GraphOptions.all_enabled()

    if not options.any_enabled():
        print("\nNo graphs selected for generation")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)
    graphs_dir = OUTPUT_DIR / "graphs"
    graphs_dir.mkdir(exist_ok=True)

    print("\nGenerating graphs")
    data = _prepare_graph_data(months)

    # Map options to generator functions
    graph_generators: list[tuple[bool, Callable[..., None], tuple[Any, ...]]] = [
        (options.activity, generate_activity_graph, (months, graphs_dir, data)),
        (options.mood_trends, generate_mood_trends_graph, (months, graphs_dir, data)),
        (options.genres_by_year, generate_genres_by_year_graph, (months, graphs_dir)),
        (options.genres_overall, generate_genres_overall_graph, (months, graphs_dir)),
        (options.mood_timeline, generate_mood_timeline_graph, (months, graphs_dir, data)),
        (options.top_artists, generate_top_artists_graph, (months, graphs_dir)),
        (options.day_of_week, generate_day_of_week_graph, (months, graphs_dir)),
        (options.hour_of_day, generate_hour_of_day_graph, (months, graphs_dir)),
        (options.dashboard, generate_dashboard, (months, graphs_dir, data)),
    ]

    for enabled, generator, args in graph_generators:
        if enabled:
            generator(*args)

    print(f"\nAll graphs saved to: {graphs_dir}")
