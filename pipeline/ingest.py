from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import requests

from pipeline.common import SOURCES_DIR, ensure_dirs, load_registry, write_json

EXT_BY_TYPE = {
    "jsonl": "jsonl",
    "yaml": "yaml",
    "markdown": "md",
}


def download_file(url: str, target: Path) -> None:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)


def main() -> None:
    ensure_dirs()
    registry = load_registry()
    manifest: list[dict[str, str]] = []

    for source in registry.get("sources", []):
        extension = EXT_BY_TYPE.get(source["source_type"], "txt")
        target = SOURCES_DIR / f"{source['id']}.{extension}"
        status = "ok"
        error = ""
        try:
            download_file(source["url"], target)
        except Exception as exc:  # pragma: no cover - network failures in CI
            status = "error"
            error = str(exc)
        manifest.append(
            {
                "id": source["id"],
                "benchmark": source["benchmark"],
                "source_type": source["source_type"],
                "url": source["url"],
                "parser": source.get("parser", "default_jsonl"),
                "path": str(target),
                "status": status,
                "error": error,
            }
        )

    write_json(
        SOURCES_DIR / "index.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "items": manifest,
        },
    )
    print(f"Ingest finished: {len(manifest)} sources processed")


if __name__ == "__main__":
    main()
