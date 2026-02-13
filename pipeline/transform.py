from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from pipeline.common import PROCESSED_DIR, SOURCES_DIR, ensure_dirs, read_json, write_json


TASK_DOMAIN_MAP: dict[str, str] = {
    # ── Cybersecurity ──
    "pico_ctf": "cybersecurity",
    "hackthebox": "cybersecurity",
    "root_me": "cybersecurity",
    "web_hacking": "cybersecurity",
    "sql_injection": "cybersecurity",
    "smart_contract_exploit": "cybersecurity",
    "novel_exploit": "cybersecurity",
    "vulnerability_detection": "cybersecurity",
    "blackbox": "cybersecurity",
    "palisade_crackme": "cybersecurity",
    "reverse_hash": "cybersecurity",
    "password_check": "cybersecurity",
    "spn_cryptanalysis": "cybersecurity",
    "rcrce": "cybersecurity",
    "automatic_jailbreak": "cybersecurity",
    "hash_collision": "cybersecurity",
    "anti_bot_site": "cybersecurity",
    # ── ML / AI Research ──
    "mlab": "ml_research",
    "ai_rd_fix_embedding": "ml_research",
    "ai_rd_nanogpt_chat_rl": "ml_research",
    "ai_rd_rust_codecontests_inference": "ml_research",
    "ai_rd_small_scaling_law": "ml_research",
    "ai_rd_triton_cumsum": "ml_research",
    "prune_attn_heads": "ml_research",
    "gpt2_algo_circuits": "ml_research",
    "gradient_inversion": "ml_research",
    "backdoor_image_classifier": "ml_research",
    "sparse_adversarial_perturbations": "ml_research",
    "adversarially_robust_models": "ml_research",
    "white_box_attack": "ml_research",
    "sentiment_probe": "ml_research",
    "few_shot_prompting": "ml_research",
    "inference_optimization": "ml_research",
    "acdc_bug": "ml_research",
    "lie_detector": "ml_research",
    "audio_classification": "ml_research",
    "image_labeling": "ml_research",
    # ── Software Engineering ──
    "code_completion": "software_engineering",
    "code2code": "software_engineering",
    "debug_small_libs": "software_engineering",
    "apps_dataset_debug": "software_engineering",
    "make_web_server": "software_engineering",
    "browser_test_2": "software_engineering",
    "implement_ace_oauth": "software_engineering",
    "search_server": "software_engineering",
    "esolang": "software_engineering",
    "auto_days_since": "software_engineering",
    "sadservers": "software_engineering",
    "tree_traversal_kernel": "software_engineering",
    "cuda_backtesting": "software_engineering",
    "network_routing": "software_engineering",
    "robot_control": "software_engineering",
    "uav_search": "software_engineering",
    "oxdna_simple": "software_engineering",
    "acronym_chatbot": "software_engineering",
    # ── Data Science & Research ──
    "data_cleaning_arjun": "data_analysis",
    "data_deduplication": "data_analysis",
    "munge_data": "data_analysis",
    "detect_data_tampering": "data_analysis",
    "interpret_data": "data_analysis",
    "interpret_building_data": "data_analysis",
    "hypothesis_testing": "data_analysis",
    "env_scientist": "data_analysis",
    "symbolic_regression": "data_analysis",
    "molecule_structure": "data_analysis",
    "iclr_authors": "data_analysis",
    "local_research": "data_analysis",
    "local_research_tex": "data_analysis",
    "wikipedia_research": "data_analysis",
    "credit_card_validity": "data_analysis",
    "file_recovery": "data_analysis",
    "file_selection": "data_analysis",
    "multiarmed_bandit": "data_analysis",
    # ── General Reasoning ──
    "arithmetic": "reasoning",
    "continue_pattern": "reasoning",
    "count_words": "reasoning",
    "request_routing": "reasoning",
    "alert_triage": "reasoning",
    "questions": "reasoning",
}


def infer_domain(text: str) -> str:
    task_family = (text or "").strip().split()[0] if text else ""
    if task_family in TASK_DOMAIN_MAP:
        return TASK_DOMAIN_MAP[task_family]
    value = (text or "").lower()
    if any(k in value for k in ("cyber", "ctf", "reverse_eng")):
        return "cybersecurity"
    if any(k in value for k in ("swe", "software", "devops", "debug")):
        return "software_engineering"
    if any(k in value for k in ("reason", "math", "logic")):
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

    tokens_count = run.get("tokens_count")
    generation_cost = run.get("generation_cost")

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
        "tokens_count": float(tokens_count) if tokens_count not in (None, "") else None,
        "generation_cost": float(generation_cost) if generation_cost not in (None, "") else None,
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
