# Last.fm Scrobble Analyzer

Analyzes your Last.fm listening history by genre, mood, and patterns over time. Fetches scrobble data from the Last.fm API and generates visualizations and reports.

## Features

- Fetch and cache scrobble history from Last.fm
- Analyze listening patterns by month, day of week, and hour
- Categorize music by genre and mood
- Generate visualizations (graphs and dashboards) 
- Export data to CSV for further analysis

## Requirements

- Python 3.10+
- Last.fm account and API key ([Create one here](https://www.last.fm/api/account/create))

## Installation

```bash
# Install the package in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Usage

Run the analyzer as a Python module:

```bash
python -m scrobble_analysis --username YOUR_USERNAME --api-key YOUR_API_KEY

# Short flags
python -m scrobble_analysis -u YOUR_USERNAME -k YOUR_API_KEY
```

If your Python Scripts directory is in your PATH, you can also use the command directly:

```bash
scrobble-analysis -u YOUR_USERNAME -k YOUR_API_KEY
```

### Options

| Flag | Description |
|------|-------------|
| `-u`, `--username` | Last.fm username |
| `-k`, `--api-key` | Last.fm API key |
| `--since` | Start date for scrobbles (YYYY-MM-DD) |
| `--no-cache` | Ignore cached data, fetch fresh from API |
| `--no-graphs` | Skip graph generation |
| `--graphs` | Comma-separated list of specific graphs to generate |
| `--no-report` | Skip console report |
| `--no-csv` | Skip CSV export |

### Available Graphs

- `activity` - Scrobble activity over time
- `mood_trends` - Mood distribution trends
- `genres_by_year` - Genre breakdown by year
- `genres_overall` - Overall genre distribution
- `mood_timeline` - Mood changes over time
- `top_artists` - Most listened artists
- `day_of_week` - Listening patterns by day
- `hour_of_day` - Listening patterns by hour
- `dashboard` - Summary dashboard with multiple charts

### Examples

```bash
# Analyze all scrobbles, generate all graphs
python -m scrobble_analysis -u USERNAME -k YOUR_API_KEY
scrobble-analysis -u USERNAME -k YOUR_API_KEY

# Analyze from a specific date
python -m scrobble_analysis -u USERNAME -k YOUR_API_KEY --since 2024-01-01
scrobble-analysis -u USERNAME -k YOUR_API_KEY --since 2024-01-01

# Only generate specific graphs
python -m scrobble_analysis -u USERNAME -k YOUR_API_KEY --graphs dashboard,top_artists
scrobble-analysis -u USERNAME -k YOUR_API_KEY --graphs dashboard,top_artists

# Data only, no visualizations
python -m scrobble_analysis -u USERNAME -k YOUR_API_KEY --no-graphs
scrobble-analysis -u USERNAME -k YOUR_API_KEY --no-graphs
```

## GitHub Actions

This project includes GitHub Actions workflows for CI and running analyses.

### Setup

1. Go to repository Settings > Secrets and variables > Actions
2. Add the following:
   - **Secret**: `LASTFM_API_KEY` - Your Last.fm API key
   - **Variable**: `LASTFM_USERNAME` - Your Last.fm username

### Workflows

- **CI** (`ci.yml`) - Runs on push/PR: linting, type checking, security scanning
- **Analyze Scrobbles** (`analyze.yml`) - Manual trigger to run analysis and upload artifacts

## Project Structure

```
scrobbles/
├── src/scrobble_analysis/      # Python package
│   ├── __init__.py             # Package exports
│   ├── __main__.py             # Module entry point
│   ├── cli.py                  # CLI and argument parsing
│   ├── api.py                  # Last.fm API client
│   ├── cache.py                # Caching for API responses
│   ├── config.py               # Configuration and constants
│   ├── analysis.py             # Data analysis functions
│   ├── visualization.py        # Graph generation
│   └── reporting.py            # Report and CSV generation
├── tests/                      # Test suite
├── pyproject.toml              # Package config and tool settings
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── .github/                    # GitHub Actions
│   ├── workflows/
│   │   ├── ci.yml              # CI pipeline
│   │   └── analyze.yml         # Analysis workflow
│   └── actions/
│       └── setup-python/       # Reusable setup action
└── .gitignore
```

## Module Descriptions

| Module | Purpose |
|--------|---------|
| `cli.py` | CLI entry point, argument parsing, orchestrates the analysis pipeline |
| `api.py` | Handles Last.fm API requests, fetches scrobbles and artist info |
| `cache.py` | Manages JSON cache files to avoid redundant API calls |
| `config.py` | Constants, paths, mood mappings, and color schemes |
| `analysis.py` | Groups scrobbles by month, calculates genres and moods |
| `visualization.py` | Generates matplotlib graphs and dashboards |
| `reporting.py` | Creates markdown reports and CSV exports |

## Output

After running, results are saved to `output/`:

- `analysis_report.md` - Detailed markdown report
- `monthly_analysis.csv` - Month-by-month data
- `all_scrobbles.csv` - Complete scrobble history
- `graphs/` - PNG visualizations

Cache files are stored in the project root:
- `scrobble_cache.json` - Cached scrobble data
- `genre_cache.json` - Cached genre lookups
