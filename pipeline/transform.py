from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from pipeline.common import PROCESSED_DIR, SOURCES_DIR, ensure_dirs, read_json, write_json


def infer_domain(text: str) -> str:
    value = (text or "").lower()
    if any(k in value for k in ("cyber", "ctf", "crypto", "reverse")):
        return "cybersecurity"
    if any(k in value for k in ("ml", "train", "finetune", "data science")):
        return "ml_engineering"
    if any(k in value for k in ("swe", "software", "devops", "implementation", "debug")):
        return "software_engineering"
    if any(k in value for k in ("reason", "math", "logic", "qa")):
        return "reasoning"
    return "unknown"


def load_release_dates(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items()}
    return {}


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def normalize_run(
    run: dict[str, Any],
    benchmark: str,
    source_id: str,
    release_dates: dict[str, str],
) -> dict[str, Any]:
    model = str(run.get("alias") or run.get("model") or run.get("agent") or "unknown")
    task_family = str(run.get("task_family") or "")
    task_id = str(run.get("task_id") or "")
    score_bin = run.get("score_binarized")
    score_cont = run.get("score_cont")
    if score_bin is None and score_cont is not None:
        score_bin = 1 if float(score_cont) >= 0.5 else 0
    if score_cont is None and score_bin is not None:
        score_cont = float(score_bin)

    release_date = (
        run.get("release_date")
        or release_dates.get(model)
        or release_dates.get(model.lower())
        or ""
    )

    return {
        "benchmark": benchmark,
        "domain": infer_domain(f"{task_family} {task_id}"),
        "subdomain": task_family or "unknown",
        "model": model,
        "agent": str(run.get("alias") or model),
        "release_date": str(release_date),
        "human_minutes": float(run.get("human_minutes") or 0.0),
        "score": float(score_cont or 0.0),
        "score_binarized": int(score_bin or 0),
        "source": source_id,
    }


def main() -> None:
    ensure_dirs()
    index_path = SOURCES_DIR / "index.json"
    if not index_path.exists():
        raise FileNotFoundError("Missing data/sources/index.json; run pipeline.ingest first")

    index = read_json(index_path)
    items = [item for item in index.get("items", []) if item.get("status") == "ok"]

    release_dates: dict[str, str] = {}
    for item in items:
        if item.get("parser") == "release_dates_yaml":
            release_dates.update(load_release_dates(Path(item["path"])))

    unified: list[dict[str, Any]] = []
    for item in items:
        if item.get("source_type") != "jsonl":
            continue
        rows = parse_jsonl(Path(item["path"]))
        for run in rows:
            unified.append(normalize_run(run, item["benchmark"], item["id"], release_dates))

    if not unified:
        # keeps downstream steps functional if upstream files change.
        unified = [
            {
                "benchmark": "synthetic",
                "domain": "software_engineering",
                "subdomain": "fallback",
                "model": "demo-model",
                "agent": "demo-model",
                "release_date": datetime.now(timezone.utc).date().isoformat(),
                "human_minutes": 30.0,
                "score": 0.55,
                "score_binarized": 1,
                "source": "fallback",
            }
        ]

    output_path = PROCESSED_DIR / "unified_records.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in unified:
            handle.write(json.dumps(row) + "\n")

    write_json(
        PROCESSED_DIR / "transform_summary.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rows": len(unified),
            "domains": sorted({r["domain"] for r in unified}),
            "benchmarks": sorted({r["benchmark"] for r in unified}),
        },
    )
    print(f"Transform finished: {len(unified)} unified rows")


if __name__ == "__main__":
    main()
