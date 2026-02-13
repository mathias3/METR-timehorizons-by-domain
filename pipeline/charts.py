"""Generate static PNG charts for the README from site/data.json."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pipeline.common import SITE_DIR

CHARTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "charts"

DOMAIN_LABELS = {
    "cybersecurity": "Cybersecurity",
    "ml_research": "ML / AI Research",
    "software_engineering": "Software Eng.",
    "data_analysis": "Data & Research",
    "reasoning": "Reasoning",
    "unknown": "General / Other",
}

DOMAIN_COLORS = {
    "cybersecurity": "#e63946",
    "ml_research": "#457b9d",
    "software_engineering": "#2a9d8f",
    "data_analysis": "#f4a261",
    "reasoning": "#e9c46a",
    "unknown": "#6c757d",
}


def _load_data() -> dict:
    path = SITE_DIR / "data.json"
    return json.loads(path.read_text())


def _label(domain: str) -> str:
    return DOMAIN_LABELS.get(domain, domain)


def _color(domain: str) -> str:
    return DOMAIN_COLORS.get(domain, "#333333")


def _fmt_minutes(minutes: float) -> str:
    if minutes >= 60:
        return f"{minutes / 60:.1f} h"
    return f"{minutes:.0f} min"


def _apply_style(fig: plt.Figure, ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")


# ── Chart 1: Domain horizon bars ──────────────────────────────────────────────

def chart_domain_horizons(data: dict) -> Path:
    horizons = sorted(data["domain_horizons"], key=lambda d: d["horizon_p50_minutes"], reverse=True)
    domains = [_label(h["domain"]) for h in horizons]
    values = [h["horizon_p50_minutes"] for h in horizons]
    colors = [_color(h["domain"]) for h in horizons]
    lo = [max(h["horizon_p50_minutes"] - h["horizon_ci_low_minutes"], 0) for h in horizons]
    hi = [max(h["horizon_ci_high_minutes"] - h["horizon_p50_minutes"], 0) for h in horizons]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(domains, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.errorbar(values, domains, xerr=[lo, hi], fmt="none", ecolor="#333", capsize=4, linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                _fmt_minutes(val), va="center", fontsize=10, color="#333")

    ax.set_xlabel("Time Horizon (minutes)", fontsize=11)
    ax.set_title("How Long Can Today's Best AI Work Autonomously?", fontsize=13, fontweight="bold", pad=12)
    ax.invert_yaxis()
    _apply_style(fig, ax)
    ax.set_xlim(0, max(values) * 1.25)

    out = CHARTS_DIR / "domain_horizons.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


# ── Chart 2: Success curves per domain ────────────────────────────────────────

def chart_success_curves(data: dict) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))

    # Aggregate curves by domain (average across models)
    domain_curves: dict[str, dict[float, list[float]]] = {}
    for curve in data.get("curves", []):
        dom = curve["domain"]
        if dom not in domain_curves:
            domain_curves[dom] = {}
        for pt in curve["points"]:
            m = pt["minutes"]
            domain_curves[dom].setdefault(m, []).append(pt["success"])

    for dom in sorted(domain_curves.keys()):
        pts = domain_curves[dom]
        xs = sorted(pts.keys())
        ys = [sum(pts[x]) / len(pts[x]) for x in xs]
        # Filter to positive minutes
        pairs = [(x, y) for x, y in zip(xs, ys) if x > 0]
        if not pairs:
            continue
        xs_f, ys_f = zip(*pairs)
        ax.plot(xs_f, ys_f, marker="o", markersize=3, linewidth=2,
                label=_label(dom), color=_color(dom), alpha=0.85)

    ax.axhline(0.5, color="#999", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(0.02, 0.52, "50 % success", transform=ax.get_yaxis_transform(),
            fontsize=8, color="#999")

    ax.set_xscale("log", base=2)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: _fmt_minutes(x) if x >= 1 else f"{x * 60:.0f}s"))
    ax.set_xlabel("Task Duration (human time)", fontsize=11)
    ax.set_ylabel("Average Success Rate", fontsize=11)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("At What Task Length Does AI Start Failing?", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    _apply_style(fig, ax)

    out = CHARTS_DIR / "success_curves.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


# ── Chart 3: Model comparison across domains ─────────────────────────────────

def chart_model_comparison(data: dict) -> Path:
    model_domain = data.get("model_domain", [])
    if not model_domain:
        return _empty_chart("model_comparison.png", "No model-domain data available")

    # Pick top models by max horizon across any domain (exclude human)
    model_max: dict[str, float] = {}
    for row in model_domain:
        if row["model"].lower() == "human":
            continue
        model_max[row["model"]] = max(model_max.get(row["model"], 0), row["horizon_minutes"])

    top_models = sorted(model_max, key=model_max.get, reverse=True)[:8]

    domains_seen = sorted({r["domain"] for r in model_domain})

    fig, ax = plt.subplots(figsize=(10, 5))
    bar_width = 0.8 / max(len(domains_seen), 1)

    for i, dom in enumerate(domains_seen):
        vals = []
        for model in top_models:
            match = [r for r in model_domain if r["model"] == model and r["domain"] == dom]
            vals.append(match[0]["horizon_minutes"] if match else 0)
        positions = [j + i * bar_width for j in range(len(top_models))]
        ax.bar(positions, vals, bar_width, label=_label(dom), color=_color(dom), edgecolor="white", linewidth=0.3)

    ax.set_xticks([j + bar_width * (len(domains_seen) - 1) / 2 for j in range(len(top_models))])
    ax.set_xticklabels([m.replace(" (Inspect)", "") for m in top_models], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Time Horizon (minutes)", fontsize=11)
    ax.set_title("Which Models Last Longest — and in Which Domains?",
                 fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    _apply_style(fig, ax)

    out = CHARTS_DIR / "model_comparison.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def _empty_chart(name: str, msg: str) -> Path:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=12, color="#999")
    ax.axis("off")
    out = CHARTS_DIR / name
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    data = _load_data()

    p1 = chart_domain_horizons(data)
    print(f"  ✓ {p1}")
    p2 = chart_success_curves(data)
    print(f"  ✓ {p2}")
    p3 = chart_model_comparison(data)
    print(f"  ✓ {p3}")
    print("Charts generated.")


if __name__ == "__main__":
    main()
