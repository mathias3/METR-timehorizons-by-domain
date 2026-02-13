from __future__ import annotations

import json
from datetime import datetime, timezone

from pipeline.common import PROCESSED_DIR, SITE_DIR, ensure_dirs, read_json, write_json


def main() -> None:
    ensure_dirs()
    fits = read_json(PROCESSED_DIR / "fits.json")

    sample_records = []
    unified_path = PROCESSED_DIR / "unified_records.jsonl"
    if unified_path.exists():
        for i, line in enumerate(unified_path.read_text().splitlines()):
            if i >= 500:
                break
            if line.strip():
                sample_records.append(json.loads(line))

    domain_by_name = {item["domain"]: item for item in fits.get("domain_horizons", [])}

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domain_horizons": fits.get("domain_horizons", []),
        "model_domain": fits.get("model_domain", []),
        "curves": fits.get("curves", []),
        "table_rows": sample_records,
        "meta": {
            "domains": sorted(domain_by_name.keys()),
            "rows": len(sample_records),
        },
    }

    write_json(SITE_DIR / "data.json", payload)
    print("Export finished: site/data.json updated")


if __name__ == "__main__":
    main()
