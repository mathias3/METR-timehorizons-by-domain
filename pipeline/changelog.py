from __future__ import annotations

from datetime import datetime, timezone

from pipeline.common import PROCESSED_DIR, ensure_dirs, read_json


def main() -> None:
    ensure_dirs()
    fits = read_json(PROCESSED_DIR / "fits.json")
    domains = sorted({row["domain"] for row in fits.get("domain_horizons", [])})
    models = sorted({row["model"] for row in fits.get("model_domain", [])})

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        f"## {stamp}",
        f"- domains: {', '.join(domains) if domains else 'none'}",
        f"- model_count: {len(models)}",
        f"- sample_models: {', '.join(models[:10]) if models else 'none'}",
        "",
    ]

    path = PROCESSED_DIR / "update_log.md"
    existing = path.read_text() if path.exists() else ""
    path.write_text("\n".join(lines) + existing)
    print("Changelog updated: data/processed/update_log.md")


if __name__ == "__main__":
    main()
