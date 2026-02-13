from __future__ import annotations

import json
from datetime import datetime, timezone

from pipeline.common import PROCESSED_DIR, SITE_DIR, ensure_dirs, read_json, write_json


# Approximate list prices ($ per 1M tokens) used only for scenario estimates.
# These are intentionally explicit and easy to update.
MODEL_PRICING_PER_1M = {
    "Claude 3 Opus (Inspect)": {"input": 15.0, "output": 75.0},
    "Claude 3.5 Sonnet (New) (Inspect)": {"input": 3.0, "output": 15.0},
    "Claude 3.5 Sonnet (Old) (Inspect)": {"input": 3.0, "output": 15.0},
    "Claude 3.7 Sonnet (Inspect)": {"input": 3.0, "output": 15.0},
    "Claude 4 Opus (Inspect)": {"input": 15.0, "output": 75.0},
    "Claude 4.1 Opus (Inspect)": {"input": 15.0, "output": 75.0},
    "Claude Opus 4.5 (Inspect)": {"input": 5.0, "output": 25.0},
    "GPT-4 0314": {"input": 30.0, "output": 60.0},
    "GPT-4 1106 (Inspect)": {"input": 10.0, "output": 30.0},
    "GPT-4 Turbo (Inspect)": {"input": 10.0, "output": 30.0},
    "GPT-4o (Inspect)": {"input": 2.5, "output": 10.0},
    "GPT-5 (Inspect)": {"input": 1.25, "output": 10.0},
    "GPT-5.1-Codex-Max (Inspect)": {"input": 1.25, "output": 10.0},
    "GPT-5.2": {"input": 1.75, "output": 10.0},
    "Gemini 3 Pro": {"input": 2.0, "output": 12.0},
    "o1 (Inspect)": {"input": 15.0, "output": 60.0},
    "o1-preview": {"input": 15.0, "output": 60.0},
    "o3 (Inspect)": {"input": 2.0, "output": 8.0},
}

SPLIT_PRESETS = {
    "input_50_output_50": {
        "input_share": 0.5,
        "output_share": 0.5,
        "label": "Balanced 50/50",
    },
    "input_70_output_30": {
        "input_share": 0.7,
        "output_share": 0.3,
        "label": "Input-heavy 70/30",
    },
    "input_90_output_10": {
        "input_share": 0.9,
        "output_share": 0.1,
        "label": "Context-heavy 90/10",
    },
}

PRICING_SOURCES = [
    "https://openai.com/api/pricing/",
    "https://platform.claude.com/docs/en/about-claude/pricing",
    "https://cloud.google.com/vertex-ai/generative-ai/pricing",
]

SPLIT_RATIONALE_SOURCES = [
    "https://platform.openai.com/docs/guides/prompt-caching",
    "https://developers.openai.com/cookbook/examples/prompt_caching101/",
]


def _load_jsonl(path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _build_agent_economics(rows: list[dict]) -> dict:
    by_model: dict[str, dict] = {}

    for row in rows:
        model = str(row.get("model") or "")
        if not model or model.lower() == "human":
            continue

        tokens = row.get("tokens_count")
        minutes = float(row.get("human_minutes") or 0.0)
        success = int(row.get("score_binarized") or 0)
        generation_cost = row.get("generation_cost")

        if model not in by_model:
            by_model[model] = {
                "model": model,
                "domains": set(),
                "runs_total": 0,
                "runs_with_tokens": 0,
                "runs_success": 0,
                "tokens_total": 0.0,
                "minutes_total": 0.0,
                "tokens_success": 0.0,
                "minutes_success": 0.0,
                "empirical_blended_rates": [],
            }

        item = by_model[model]
        item["runs_total"] += 1
        item["domains"].add(str(row.get("domain") or "unknown"))

        if isinstance(tokens, (int, float)) and tokens > 0 and minutes > 0:
            item["runs_with_tokens"] += 1
            item["tokens_total"] += float(tokens)
            item["minutes_total"] += minutes
            if success == 1:
                item["runs_success"] += 1
                item["tokens_success"] += float(tokens)
                item["minutes_success"] += minutes

            if isinstance(generation_cost, (int, float)) and generation_cost > 0:
                item["empirical_blended_rates"].append(float(generation_cost) / float(tokens) * 1_000_000)

    models = []
    for item in by_model.values():
        tokens_per_min = (
            item["tokens_total"] / item["minutes_total"] if item["minutes_total"] > 0 else None
        )
        tokens_per_success_min = (
            item["tokens_success"] / item["minutes_success"] if item["minutes_success"] > 0 else None
        )

        pricing = MODEL_PRICING_PER_1M.get(item["model"])
        cost_estimates = {}
        if pricing and tokens_per_success_min is not None:
            for key, preset in SPLIT_PRESETS.items():
                blended = preset["input_share"] * pricing["input"] + preset["output_share"] * pricing["output"]
                usd_per_success_hour = tokens_per_success_min * 60.0 * blended / 1_000_000
                cost_estimates[key] = {
                    "blended_usd_per_1m_tokens": blended,
                    "usd_per_autonomous_hour": usd_per_success_hour,
                }

        models.append(
            {
                "model": item["model"],
                "domains": sorted(item["domains"]),
                "runs_total": item["runs_total"],
                "runs_with_tokens": item["runs_with_tokens"],
                "runs_success": item["runs_success"],
                "tokens_per_minute": tokens_per_min,
                "tokens_per_hour": tokens_per_min * 60.0 if tokens_per_min is not None else None,
                "tokens_per_success_minute": tokens_per_success_min,
                "tokens_per_success_hour": tokens_per_success_min * 60.0 if tokens_per_success_min is not None else None,
                "assumed_price_usd_per_1m": pricing,
                "empirical_blended_usd_per_1m_from_runs": (
                    sum(item["empirical_blended_rates"]) / len(item["empirical_blended_rates"])
                    if item["empirical_blended_rates"]
                    else None
                ),
                "estimated_cost_scenarios": cost_estimates,
            }
        )

    models.sort(
        key=lambda m: m["tokens_per_success_hour"]
        if m["tokens_per_success_hour"] is not None
        else float("inf")
    )

    return {
        "models": models,
        "split_presets": SPLIT_PRESETS,
        "pricing_sources": PRICING_SOURCES,
        "split_rationale_sources": SPLIT_RATIONALE_SOURCES,
        "notes": [
            "tokens_count in source data is total tokens and does not expose input/output split",
            "cost scenarios are estimates based on assumed input/output split presets",
            "use tokens_per_success_hour as assumption-free metric for model efficiency",
        ],
    }


def main() -> None:
    ensure_dirs()
    fits = read_json(PROCESSED_DIR / "fits.json")
    unified_rows = _load_jsonl(PROCESSED_DIR / "unified_records.jsonl")

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
        "agent_economics": _build_agent_economics(unified_rows),
        "meta": {
            "domains": sorted(domain_by_name.keys()),
            "rows": len(sample_records),
        },
    }

    write_json(SITE_DIR / "data.json", payload)
    print("Export finished: site/data.json updated")


if __name__ == "__main__":
    main()
