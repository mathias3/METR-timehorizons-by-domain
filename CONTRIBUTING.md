# Contributing

Thanks for improving the tracker.

## Add a new benchmark source

1. Add an entry to `data/benchmarks.yaml`:

```yaml
- id: my_benchmark_runs
  benchmark: my_benchmark
  source_repo: org/repo
  source_type: jsonl
  url: https://raw.githubusercontent.com/org/repo/main/path/to/file.jsonl
  parser: default_jsonl
```

2. If the format is custom, add a parser in `pipeline/transform.py`.
3. Run:

```bash
python -m pipeline.ingest
python -m pipeline.transform
python -m pipeline.fit
python -m pipeline.changelog
python -m pipeline.export
python -m pytest -q
```

4. Open a PR with:
- source URL and license notes,
- rationale for domain mapping,
- before/after screenshot of charts if UI changed.

## Data expectations

Unified records use these fields:
`benchmark, domain, subdomain, model, agent, release_date, human_minutes, score, score_binarized, source`

## Style

- Keep changes focused.
- Prefer explicit data transformations.
- Add tests for parser and fit behavior.
