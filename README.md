# Sophia Justice Agent v4.0 — Forensic Screening Demo

Password-gated web demo of the Sophia forensic PDF screening engine.

## Deploy
1. Push to GitHub
2. Import on vercel.com (framework: Other)
3. Set env vars: `SOPHIA_PASSWORD`, `SOPHIA_SECRET`
4. Deploy

## Modules
- `api/sophia/engine.py`     — orchestrator
- `api/sophia/extract.py`    — PDF/text extraction
- `api/sophia/benford.py`    — Benford's Law
- `api/sophia/redflags.py`   — red-flag detection
- `api/sophia/title.py`      — title-search parsing
- `api/sophia/report.py`     — branded HTML report
