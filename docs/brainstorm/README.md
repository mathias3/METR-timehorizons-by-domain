# METR Cross-Domain Time Horizon Tracker

Auto-updating, interactive tracking of AI time horizons across domains and benchmarks.

## Why this project

METR already published cross-domain analyses, but those are mostly point-in-time artifacts. This repo adds:
- automated refreshes from upstream benchmark sources,
- a unified dataset for downstream analysis,
- interactive visualizations on a static site,
- a contribution path for adding new benchmarks.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m pipeline.ingest
python -m pipeline.transform
python -m pipeline.fit
python -m pipeline.export
```

Open `site/index.html` in a browser (or serve the folder) to explore charts.

## Data flow

1. `pipeline.ingest` downloads raw benchmark inputs into `data/sources/`
2. `pipeline.transform` normalizes records into `data/processed/unified_records.jsonl`
3. `pipeline.fit` computes domain-level horizon proxies + growth estimates into `data/processed/fits.json`
4. `pipeline.export` writes `site/data.json` for the frontend

## Auto-updates

GitHub Actions workflow: `.github/workflows/update.yml`
- runs weekly and on manual trigger,
- refreshes data + site artifacts,
- commits changes if outputs changed,
- publishes `site/` to GitHub Pages.

## Repository layout

- `pipeline/` Python pipeline modules
- `data/` source, processed, snapshots, and registry config
- `site/` static Plotly.js app
- `tests/` lightweight unit tests
- `docs/brainstorm/` preserved original idea notes

## License

MIT
