from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re

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


def get_latest_metr_report() -> str:
    """Find the latest time-horizon-X-Y report from METR repo."""
    try:
        # List all directories in /reports/
        api_url = "https://api.github.com/repos/METR/eval-analysis-public/contents/reports"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        items = response.json()
        if not isinstance(items, list):
            raise ValueError("Unexpected API response format")
        
        # Filter for time-horizon-* directories and sort by version
        report_dirs = []
        for item in items:
            if item.get("type") == "dir" and item.get("name", "").startswith("time-horizon-"):
                name = item["name"]
                # Extract version numbers (e.g., "time-horizon-1-1" -> (1, 1))
                match = re.match(r"time-horizon-(\d+)-(\d+)", name)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    report_dirs.append((major, minor, name))
        
        if not report_dirs:
            print("Warning: No time-horizon directories found, falling back to time-horizon-1-1")
            return "time-horizon-1-1"
        
        # Sort by version numbers (major, minor) and take the latest
        report_dirs.sort(key=lambda x: (x[0], x[1]))
        latest = report_dirs[-1][2]
        print(f"Detected latest METR report: {latest}")
        return latest
        
    except Exception as exc:
        print(f"Warning: Failed to detect latest METR report ({exc}), falling back to time-horizon-1-1")
        return "time-horizon-1-1"


def main() -> None:
    ensure_dirs()
    registry = load_registry()
    manifest: list[dict[str, str]] = []
    
    # Get latest METR report version once
    latest_report = get_latest_metr_report()

    for source in registry.get("sources", []):
        extension = EXT_BY_TYPE.get(source["source_type"], "txt")
        target = SOURCES_DIR / f"{source['id']}.{extension}"
        status = "ok"
        error = ""
        
        # Handle dynamic METR report URLs
        url = source["url"]
        if "{LATEST_REPORT}" in url:
            url = url.replace("{LATEST_REPORT}", latest_report)
        
        try:
            download_file(url, target)
        except Exception as exc:  # pragma: no cover - network failures in CI
            status = "error"
            error = str(exc)
        
        manifest.append(
            {
                "id": source["id"],
                "benchmark": source["benchmark"],
                "source_type": source["source_type"],
                "url": url,  # Store the actual URL used
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
            "latest_metr_report": latest_report,
            "items": manifest,
        },
    )
    print(f"Ingest finished: {len(manifest)} sources processed (latest METR: {latest_report})")


if __name__ == "__main__":
    main()
