"""
Report generation functions for scrobble analysis.
"""

import csv
from collections import defaultdict

from .config import OUTPUT_DIR, WINDOW_SIZE

__all__ = ["generate_report", "export_to_csv"]

# Month name lookup (index 0 is empty for 1-based month numbers)
MONTH_NAMES: tuple[str, ...] = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def _collect_track_stats(months: list[dict]) -> tuple[set[str], set[tuple[str, str]]]:
    """Collect unique artists and tracks from all months"""
    all_artists: set[str] = set()
    all_tracks: set[tuple[str, str]] = set()

    for month in months:
        for track in month["tracks"]:
            all_artists.add(track["artist"])
            all_tracks.add((track["artist"], track["track"]))

    return all_artists, all_tracks


def _print_section(title: str) -> None:
    """Print a section header"""
    print("\n" + "-" * WINDOW_SIZE)
    print(title)
    print("-" * WINDOW_SIZE)


def generate_report(months: list[dict]) -> list[dict]:
    """
    Generate analysis report to console

    Args:
        months: List of month dictionaries with analysis data

    Returns:
        The input months (for chaining)
    """
    print("\n" + "=" * WINDOW_SIZE)
    print("LAST.FM SCROBBLE ANALYSIS REPORT")
    print("=" * WINDOW_SIZE)

    # Summary statistics
    total_scrobbles = sum(m["size"] for m in months)
    all_artists, all_tracks = _collect_track_stats(months)

    print(f"\nTotal months analyzed: {len(months)}")
    print(f"Total scrobbles: {total_scrobbles}")
    print(f"Unique artists: {len(all_artists)}")
    print(f"Unique tracks: {len(all_tracks)}")
    print(
        f"Date range: {MONTH_NAMES[months[0]['month']]} {months[0]['year']} - "
        f"{MONTH_NAMES[months[-1]['month']]} {months[-1]['year']}"
    )
    print(f"Average scrobbles per month: {total_scrobbles / len(months):.1f}")

    _print_section("YEARLY ANALYSIS")

    yearly_data: dict = defaultdict(
        lambda: {
            "scrobbles": 0,
            "months": 0,
            "genres": defaultdict(int),
            "moods": defaultdict(int),
        }
    )

    for month in months:
        year = month["year"]
        yearly_data[year]["scrobbles"] += month["size"]
        yearly_data[year]["months"] += 1
        for genre, count in month.get("genre_distribution", {}).items():
            yearly_data[year]["genres"][genre] += count
        for mood, count in month.get("mood_distribution", {}).items():
            yearly_data[year]["moods"][mood] += count

    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        top_genres = sorted(data["genres"].items(), key=lambda x: -x[1])[:5]
        top_moods = sorted(data["moods"].items(), key=lambda x: -x[1])[:3]

        print(f"\n{year}:")
        print(f"Months: {data['months']}")
        print(f"Total scrobbles: {data['scrobbles']}")
        print(f"Avg scrobbles/month: {data['scrobbles'] / data['months']:.1f}")
        if top_genres:
            print(f"Top genres: {', '.join(g[0] for g in top_genres)}")
        if top_moods:
            print(f"Mood breakdown: {', '.join(f'{m[0]}({m[1]})' for m in top_moods)}")

    _print_section("MONTHLY BREAKDOWN")

    current_year = None
    for month in months:
        if month["year"] != current_year:
            current_year = month["year"]
            print(f"\n--- {current_year} ---")

        month_name = MONTH_NAMES[month["month"]]
        top_genres = list(month.get("genre_distribution", {}).keys())[:3]

        print(f"\n{month_name}:")
        print(f"Scrobbles: {month['size']}")
        print(f"Primary mood: {month.get('primary_mood', 'unknown')}")
        if top_genres:
            print(f"Top genres: {', '.join(top_genres)}")

    _print_section("LISTENING ACTIVITY TRENDS")

    sizes = [m["size"] for m in months]
    print(f"\nQuietest month: {min(sizes)} scrobbles")
    print(f"Most active month: {max(sizes)} scrobbles")
    print(f"Average: {sum(sizes) / len(sizes):.1f} scrobbles/month")

    # Activity visualization
    print("\nScrobbles by month (scaled):")
    max_size = max(sizes)
    for month in months:
        bar_len = int((month["size"] / max_size) * 30)
        bar = "|" * bar_len
        print(f"{month['month']:2}/{month['year']}: {bar} ({month['size']})")

    _print_section("MOOD TRENDS OVER TIME")

    print("\nPrimary mood by month:")
    for month in months:
        print(
            f"{month['month']}/{month['year']}: {month.get('primary_mood', 'unknown')}"
        )

    _print_section("TOP ARTISTS (by scrobble count)")

    artist_counts: dict[str, int] = defaultdict(int)
    for month in months:
        for track in month["tracks"]:
            artist_counts[track["artist"]] += 1

    top_artists = sorted(artist_counts.items(), key=lambda x: -x[1])[:20]
    for artist, count in top_artists:
        print(f"{artist}: {count} scrobbles")

    _print_section("TOP TRACKS (by scrobble count)")

    track_counts: dict[tuple[str, str], int] = defaultdict(int)
    for month in months:
        for track in month["tracks"]:
            track_counts[(track["artist"], track["track"])] += 1

    top_tracks = sorted(track_counts.items(), key=lambda x: -x[1])[:20]
    for (artist, track), count in top_tracks:
        print(f"  {track} - {artist}: {count} plays")

    return months


def export_to_csv(
    months: list[dict], output_file: str = "monthly_analysis.csv"
) -> None:
    """
    Export analysis results to CSV files.

    Creates two files:
    - monthly_analysis.csv: Summary by month
    - all_scrobbles.csv: Detailed scrobble data

    Args:
        months: List of month dictionaries with analysis data
        output_file: Name of the monthly summary file
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / output_file

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Year",
                "Month",
                "Scrobbles",
                "Primary Mood",
                "Top Genres",
                "Mood Distribution",
            ]
        )

        for month in months:
            top_genres = "; ".join(list(month.get("genre_distribution", {}).keys())[:5])
            mood_dist = "; ".join(
                f"{k}:{v}" for k, v in month.get("mood_distribution", {}).items()
            )

            writer.writerow(
                [
                    month["year"],
                    month["month"],
                    month["size"],
                    month.get("primary_mood", "unknown"),
                    top_genres,
                    mood_dist,
                ]
            )

    print(f"\nAnalysis exported to: {output_path}")

    detailed_path = OUTPUT_DIR / "all_scrobbles.csv"
    with open(detailed_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Artist", "Track", "Album", "Mood", "Genres"])

        for month in months:
            for track in month["tracks"]:
                writer.writerow(
                    [
                        track["date"],
                        track["artist"],
                        track["track"],
                        track["album"],
                        track.get("mood", "unknown"),
                        "; ".join(track.get("genres", [])[:5]),
                    ]
                )

    print(f"Detailed scrobbles exported to: {detailed_path}")
