from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SOURCES_DIR = DATA_DIR / "sources"
PROCESSED_DIR = DATA_DIR / "processed"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
SITE_DIR = ROOT / "site"


def ensure_dirs() -> None:
    for path in (SOURCES_DIR, PROCESSED_DIR, SNAPSHOTS_DIR, SITE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict[str, Any]:
    registry_path = DATA_DIR / "benchmarks.yaml"
    return yaml.safe_load(registry_path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())
