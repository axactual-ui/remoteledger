# Remote Accounting & Finance Jobs Board

Static jobs board built from REAL postings on public ATS APIs (Greenhouse, Lever, Ashby). Python 3 only.

## Files
- `companies.json` – configurable list of company board slugs per ATS (`greenhouse`, `lever`, `ashby`). Add slugs to grow the board.
- `fetch_jobs.py` – pulls every board, keeps remote accounting / bookkeeping / tax / AP-AR-payroll / FP&A / audit roles, drops anything older than 30 days (override with `MAX_AGE=`), writes `data/jobs.json`.
- `build.py` – generates `dist/`: home with search + role + US/global filters, one page per job (schema.org JobPosting JSON-LD, source, posted date, apply link to the original posting), /post-a-job/, /digest/, sitemap.xml, robots.txt.
- `refresh.sh` – daily routine: fetch + build.

## Rebuild
    ./refresh.sh
    python3 -m http.server -d dist 8002

## Build-time overrides (env vars)
SITE_NAME, SITE_URL, SQUARE_LINK_STANDARD ($49), SQUARE_LINK_FEATURED ($79/30d), SQUARE_LINK_SPONSOR ($199/mo),
SQUARE_LINK_DIGEST ($99), CONTACT_EMAIL, DIGEST_FORM_ACTION (email signup endpoint).

## Notes
- Paid employer posts: add them to a `data/paid_jobs.json` workflow later (not built yet); currently all listings are scraped from public APIs.
- Tune role keywords in `ROLE` / `EXCLUDE` in fetch_jobs.py.
- Deploy `dist/` to any static host (Vercel: build `./refresh.sh`, output `dist`).

## Config
Contact email and Square links live in config.py (env vars of the same name override).
