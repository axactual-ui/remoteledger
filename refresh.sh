#!/usr/bin/env bash
# Daily routine: fetch fresh postings (drops >30 days), rebuild site. Set SITE_NAME/SITE_URL/SQUARE_* env vars for production.
set -euo pipefail; cd "$(dirname "$0")"
python3 fetch_jobs.py
python3 build.py
