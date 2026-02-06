"""
Last.fm Scrobble Analysis Tool
Analyzes listening habits by genre, scrobble count, and mood across months.
Fetches data from Last.fm API for user scrobbles.

Usage:
    python -m scrobble_analysis --username <username> --api-key <key>
    python -m scrobble_analysis -u <username> -k <key> --no-graphs
    python -m scrobble_analysis -u <username> -k <key> --graphs activity,dashboard
"""

import argparse
import sys
from datetime import datetime, timezone

# Fix Windows console encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

from .analysis import analyze_months, group_scrobbles_by_month
from .api import fetch_scrobbles
from .config import OUTPUT_DIR, WINDOW_SIZE
from .reporting import export_to_csv, generate_report
from .visualization import GraphOptions, generate_graphs


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="scrobble-analysis",
        description="Analyze your Last.fm scrobbles by genre, mood, and listening patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m %(prog)s -u USERNAME -k YOUR_API_KEY
  python -m %(prog)s -u USERNAME -k YOUR_API_KEY --no-graphs
  python -m %(prog)s -u USERNAME -k YOUR_API_KEY --graphs activity,dashboard,top_artists
  python -m %(prog)s -u USERNAME -k YOUR_API_KEY --since 2025-06-23
        """,
    )

    # Required arguments (can also be provided interactively)
    parser.add_argument("-u", "--username", help="Last.fm username")
    parser.add_argument(
        "-k",
        "--api-key",
        help="Last.fm API key (Create one here: https://www.last.fm/api/account/create)",
    )

    # Optional arguments
    parser.add_argument(
        "--since",
        help="Start date for scrobbles (YYYY-MM-DD format). Default: fetch all",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore cached data and fetch fresh from API",
    )

    # Graph options
    graph_group = parser.add_mutually_exclusive_group()
    graph_group.add_argument(
        "--no-graphs", action="store_true", help="Skip graph generation entirely"
    )
    graph_group.add_argument(
        "--graphs",
        help="Comma-separated list of graphs to generate. "
        "Options: activity, mood_trends, genres_by_year, "
        "genres_overall, mood_timeline, top_artists, "
        "day_of_week, hour_of_day, dashboard",
    )

    # Output options
    parser.add_argument("--no-report", action="store_true", help="Skip console report generation")
    parser.add_argument("--no-csv", action="store_true", help="Skip CSV export")

    return parser.parse_args()


def get_credentials(args):
    """Get username and API key from args or prompt user."""
    username = args.username
    api_key = args.api_key

    if not username:
        username = input("Enter your Last.fm username: ").strip()
        if not username:
            print("Error: Username is required")
            sys.exit(1)

    if not api_key:
        api_key = input("Enter your Last.fm API key: ").strip()
        if not api_key:
            print("Error: API key is required")
            print("Get one at: https://www.last.fm/api/account/create")
            sys.exit(1)

    return username, api_key


def parse_graph_options(args) -> GraphOptions:
    """Parse graph options from arguments."""
    if args.no_graphs:
        return GraphOptions.none_enabled()

    if args.graphs:
        # Start with all disabled
        options = GraphOptions.none_enabled()
        requested = [g.strip().lower() for g in args.graphs.split(",")]

        graph_map = {
            "activity": "activity",
            "mood_trends": "mood_trends",
            "genres_by_year": "genres_by_year",
            "genres_overall": "genres_overall",
            "mood_timeline": "mood_timeline",
            "top_artists": "top_artists",
            "day_of_week": "day_of_week",
            "hour_of_day": "hour_of_day",
            "dashboard": "dashboard",
        }

        for graph in requested:
            if graph in graph_map:
                setattr(options, graph_map[graph], True)
            else:
                print(f"Warning: Unknown graph type '{graph}', skipping")

        return options

    # Default: all enabled
    return GraphOptions.all_enabled()


def parse_date(date_str: str):
    """Parse date string to datetime object."""
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD")
        sys.exit(1)


def main():
    args = parse_args()

    # Get credentials
    username, api_key = get_credentials(args)

    # Parse options
    from_date = parse_date(args.since)
    graph_options = parse_graph_options(args)
    use_cache = not args.no_cache

    # Header
    print("=" * WINDOW_SIZE)
    print("LAST.FM SCROBBLE ANALYZER")
    print(f"User: {username}")
    print("=" * WINDOW_SIZE)

    # Fetch scrobbles
    scrobbles = fetch_scrobbles(username, api_key, from_date=from_date, use_cache=use_cache)

    if not scrobbles:
        print("\nNo scrobbles found. Please check your username and try again.")
        return

    # Group by month
    print("\nGrouping scrobbles by month")
    months = group_scrobbles_by_month(scrobbles)
    print(f"Found {len(months)} months of data")

    # Analyze
    months = analyze_months(months, api_key)

    # Generate report
    if not args.no_report:
        generate_report(months)

    # Export to CSV
    if not args.no_csv:
        export_to_csv(months)

    # Generate graphs
    generate_graphs(months, graph_options)

    print("\n" + "=" * WINDOW_SIZE)
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("=" * WINDOW_SIZE)


if __name__ == "__main__":
    main()
