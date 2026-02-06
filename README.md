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
# Install dependencies
pip install -r config/requirements.txt
```

## Usage

### Command Line

```bash
cd python

# Basic usage (will prompt for credentials)
python scrobble_analysis.py

# With credentials
python scrobble_analysis.py --username YOUR_USERNAME --api-key YOUR_API_KEY

# Short flags
python scrobble_analysis.py -u YOUR_USERNAME -k YOUR_API_KEY
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
python scrobble_analysis.py -u USERNAME -k YOUR_API_KEY

# Analyze from a specific date
python scrobble_analysis.py -u USERNAME -k YOUR_API_KEY --since 2024-01-01

# Only generate specific graphs
python scrobble_analysis.py -u USERNAME -k YOUR_API_KEY --graphs dashboard,top_artists

# Data only, no visualizations
python scrobble_analysis.py -u USERNAME -k YOUR_API_KEY --no-graphs
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
├── python/                     # Python source code
│   ├── scrobble_analysis.py    # Main entry point and CLI
│   └── helpers/                # Module with helper functions
│       ├── __init__.py         # Package exports
│       ├── api.py              # Last.fm API client
│       ├── cache.py            # Caching for API responses
│       ├── config.py           # Configuration and constants
│       ├── analysis.py         # Data analysis functions
│       ├── visualization.py    # Graph generation
│       └── reporting.py        # Report and CSV generation
├── config/                     # Configuration files
│   ├── requirements.txt        # Runtime dependencies
│   ├── requirements-dev.txt    # Development dependencies
│   └── pyproject.toml          # Tool configuration (ruff, mypy)
├── .github/                    # GitHub Actions
│   ├── workflows/
│   │   ├── ci.yml              # CI pipeline (lint, type check, security)
│   │   └── analyze.yml         # Run analysis workflow
│   └── actions/
│       └── setup-python/       # Reusable Python setup action
└── .gitignore                  # Git ignore rules
```

## File Descriptions

### Python Source

| File | Purpose |
|------|---------|
| `scrobble_analysis.py` | CLI entry point, argument parsing, orchestrates the analysis pipeline |
| `helpers/api.py` | Handles Last.fm API requests, fetches scrobbles and artist info |
| `helpers/cache.py` | Manages JSON cache files to avoid redundant API calls |
| `helpers/config.py` | Constants, paths, mood mappings, and color schemes |
| `helpers/analysis.py` | Groups scrobbles by month, calculates genres and moods |
| `helpers/visualization.py` | Generates matplotlib graphs and dashboards |
| `helpers/reporting.py` | Creates markdown reports and CSV exports |

### Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Runtime dependencies (requests, matplotlib) |
| `requirements-dev.txt` | Dev tools (ruff, mypy, bandit) |
| `pyproject.toml` | Configuration for linting, type checking, and security scanning |

### GitHub Actions

| File | Purpose |
|------|---------|
| `ci.yml` | Runs on code changes: linting (ruff), type checking (mypy), security scan (bandit), syntax validation |
| `analyze.yml` | Manual workflow to run analysis and upload results as artifacts |
| `setup-python/action.yml` | Reusable composite action for Python environment setup with caching |

## Output

After running, results are saved to `scrobble_analysis/`:

- `analysis_report.md` - Detailed markdown report
- `monthly_analysis.csv` - Month-by-month data
- `all_scrobbles.csv` - Complete scrobble history
- `graphs/` - PNG visualizations

Cache files are stored in the project root:
- `scrobble_cache.json` - Cached scrobble data
- `genre_cache.json` - Cached genre lookups
