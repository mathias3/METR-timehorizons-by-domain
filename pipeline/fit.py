from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from statistics import median
from typing import Any

import numpy as np

from pipeline.common import PROCESSED_DIR, SNAPSHOTS_DIR, ensure_dirs, write_json


def load_unified_records() -> list[dict[str, Any]]:
    path = PROCESSED_DIR / "unified_records.jsonl"
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _safe_log2(x: float) -> float:
    return math.log2(max(x, 1e-6))


def estimate_horizon(points: list[dict[str, Any]]) -> tuple[float, float, list[dict[str, float]]]:
    # Bin by rounded log2(minutes), then estimate crossing near 50% success.
    bins: dict[int, list[int]] = defaultdict(list)
    for row in points:
        if row["human_minutes"] <= 0:
            continue
        bins[int(round(_safe_log2(float(row["human_minutes"]))))].append(int(row["score_binarized"]))

    if not bins:
        return 0.0, 0.0, []

    curve = []
    for x_bin in sorted(bins):
        ys = bins[x_bin]
        success = sum(ys) / len(ys)
        curve.append({"log2_minutes": float(x_bin), "minutes": float(2**x_bin), "success": success})

    # Enforce a non-increasing success profile with duration to reduce noise artifacts.
    running = 1.0
    for row in curve:
        running = min(running, row["success"])
        row["success_smoothed"] = running

    smoothed = [row["success_smoothed"] for row in curve]
    minutes = [row["minutes"] for row in curve]

    # Robust fallback behavior:
    # - if always >= 50%: horizon is right-censored at the maximum observed duration
    # - if always < 50%: horizon is below minimum observed duration
    if all(s >= 0.5 for s in smoothed):
        horizon = minutes[-1]
    elif all(s < 0.5 for s in smoothed):
        horizon = minutes[0]
    else:
        horizon = minutes[0]
        for i in range(len(curve) - 1):
            a, b = curve[i], curve[i + 1]
            if a["success_smoothed"] >= 0.5 and b["success_smoothed"] < 0.5:
                span = max(a["success_smoothed"] - b["success_smoothed"], 1e-6)
                frac = (a["success_smoothed"] - 0.5) / span
                log2_h = a["log2_minutes"] + frac * (b["log2_minutes"] - a["log2_minutes"])
                horizon = float(2**log2_h)
                break

    xs = np.array([p["log2_minutes"] for p in curve], dtype=float)
    ys = np.array([p["success"] for p in curve], dtype=float)
    slope = 0.0
    if len(xs) >= 2:
        slope = float(np.polyfit(xs, ys, 1)[0])

    return horizon, slope, curve


def compute_doubling_months(model_points: list[dict[str, Any]]) -> float | None:
    rows = [r for r in model_points if r.get("release_date")]
    if len(rows) < 2:
        return None

    parsed = []
    for row in rows:
        try:
            dt = datetime.fromisoformat(str(row["release_date"]).replace("Z", "+00:00"))
        except ValueError:
            try:
                dt = datetime.strptime(str(row["release_date"]), "%Y-%m-%d")
            except ValueError:
                continue
        parsed.append((dt, max(float(row["horizon_minutes"]), 1e-6)))

    if len(parsed) < 2:
        return None

    parsed.sort(key=lambda p: p[0])
    t0 = parsed[0][0]
    x = np.array([(p[0] - t0).days / 30.4375 for p in parsed], dtype=float)
    y = np.array([math.log2(p[1]) for p in parsed], dtype=float)
    slope = float(np.polyfit(x, y, 1)[0]) if len(x) >= 2 else 0.0
    if slope <= 0:
        return None
    return float(1.0 / slope)


def main() -> None:
    ensure_dirs()
    records = load_unified_records()

    grouped_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    grouped_model_domain: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for row in records:
        grouped_domain[row["domain"]].append(row)
        grouped_model_domain[(row["model"], row["domain"])].append(row)

    model_domain = []
    curves = []
    for (model, domain), points in grouped_model_domain.items():
        horizon, beta, curve = estimate_horizon(points)
        release_dates = sorted({p.get("release_date", "") for p in points if p.get("release_date")})
        model_domain.append(
            {
                "model": model,
                "domain": domain,
                "release_date": release_dates[-1] if release_dates else "",
                "horizon_minutes": round(horizon, 4),
                "beta_proxy": round(beta, 6),
                "n_points": len(points),
            }
        )
        curves.append({"model": model, "domain": domain, "points": curve})

    domain_horizons = []
    for domain, points in grouped_domain.items():
        h, _, _ = estimate_horizon(points)
        domain_models = [row for row in model_domain if row["domain"] == domain]
        horizons = [float(m["horizon_minutes"]) for m in domain_models if m["horizon_minutes"] > 0]
        low = float(np.quantile(horizons, 0.1)) if horizons else 0.0
        high = float(np.quantile(horizons, 0.9)) if horizons else 0.0
        doubling = compute_doubling_months(domain_models)
        domain_horizons.append(
            {
                "domain": domain,
                "horizon_p50_minutes": round(float(h), 4),
                "horizon_ci_low_minutes": round(low, 4),
                "horizon_ci_high_minutes": round(high, 4),
                "doubling_time_months": round(doubling, 4) if doubling else None,
                "models": len({m["model"] for m in domain_models}),
                "points": len(points),
                "median_record_minutes": round(float(median([float(p["human_minutes"]) for p in points])), 4),
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domain_horizons": sorted(domain_horizons, key=lambda x: x["domain"]),
        "model_domain": sorted(model_domain, key=lambda x: (x["domain"], x["model"])),
        "curves": curves,
    }

    write_json(PROCESSED_DIR / "fits.json", payload)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_json(SNAPSHOTS_DIR / f"fits_{stamp}.json", payload)
    print(
        f"Fit finished: {len(payload['domain_horizons'])} domains, "
        f"{len(payload['model_domain'])} model/domain rows"
    )


if __name__ == "__main__":
    main()
