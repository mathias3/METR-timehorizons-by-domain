"""Generate static PNG charts for the README from site/data.json."""
from __future__ import annotations

import json
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
    "cybersecurity": "#c85663",
    "ml_research": "#4f77b4",
    "software_engineering": "#3f9e8b",
    "data_analysis": "#d4955e",
    "reasoning": "#9a7fb8",
    "unknown": "#7a7f87",
}


def _init_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#a9b7c6",
            "axes.labelcolor": "#233243",
            "xtick.color": "#233243",
            "ytick.color": "#233243",
            "grid.color": "#e7edf4",
            "grid.linewidth": 0.8,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "font.size": 11,
        }
    )


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
    ax.spines["left"].set_color("#a9b7c6")
    ax.spines["bottom"].set_color("#a9b7c6")
    ax.grid(True, axis="y", alpha=0.9)
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

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(domains, values, color=colors, edgecolor="white", linewidth=1.2)
    ax.errorbar(values, domains, xerr=[lo, hi], fmt="none", ecolor="#4b5d71", capsize=4, linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                _fmt_minutes(val), va="center", fontsize=10, color="#233243")

    ax.set_xlabel("Time Horizon (minutes)", fontsize=12)
    ax.set_title("How Long Can Today's Best AI Work Autonomously?", fontsize=15, fontweight="bold", pad=12)
    ax.invert_yaxis()
    _apply_style(fig, ax)
    ax.set_xlim(0, max(values) * 1.25)

    out = CHARTS_DIR / "domain_horizons.png"
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


# ── Chart 2: Success curves per domain ────────────────────────────────────────

def chart_success_curves(data: dict) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5.5))

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
        ax.plot(
            xs_f,
            ys_f,
            marker="o",
            markersize=5,
            linewidth=2.8,
            label=_label(dom),
            color=_color(dom),
            alpha=0.92,
            markeredgecolor="white",
            markeredgewidth=0.7,
        )

    ax.axhline(0.5, color="#8fa1b3", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.text(0.02, 0.52, "50 % success", transform=ax.get_yaxis_transform(),
            fontsize=9, color="#75879a")

    ax.set_xscale("log", base=2)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: _fmt_minutes(x) if x >= 1 else f"{x * 60:.0f}s"))
    ax.set_xlabel("Task Duration (human time)", fontsize=12)
    ax.set_ylabel("Average Success Rate", fontsize=12)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("At What Task Length Does AI Start Failing?", fontsize=15, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
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

    fig, ax = plt.subplots(figsize=(11, 5.6))
    bar_width = 0.8 / max(len(domains_seen), 1)

    for i, dom in enumerate(domains_seen):
        vals = []
        for model in top_models:
            match = [r for r in model_domain if r["model"] == model and r["domain"] == dom]
            vals.append(match[0]["horizon_minutes"] if match else 0)
        positions = [j + i * bar_width for j in range(len(top_models))]
        ax.bar(positions, vals, bar_width, label=_label(dom), color=_color(dom), edgecolor="white", linewidth=0.9)

    ax.set_xticks([j + bar_width * (len(domains_seen) - 1) / 2 for j in range(len(top_models))])
    ax.set_xticklabels([m.replace(" (Inspect)", "") for m in top_models], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Time Horizon (minutes)", fontsize=12)
    ax.set_title("Which Models Last Longest — and in Which Domains?",
                 fontsize=15, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
    _apply_style(fig, ax)

    out = CHARTS_DIR / "model_comparison.png"
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_token_efficiency(data: dict) -> Path:
    econ = data.get("agent_economics", {})
    rows = [
        row
        for row in econ.get("models", [])
        if isinstance(row.get("tokens_per_success_hour"), (int, float))
    ]
    if not rows:
        return _empty_chart("token_efficiency.png", "No token efficiency data available")

    rows = sorted(rows, key=lambda r: r["tokens_per_success_hour"])[:10]
    models = [r["model"].replace(" (Inspect)", "") for r in rows]
    values = [r["tokens_per_success_hour"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    bars = ax.barh(models, values, color="#3f9e8b", edgecolor="white", linewidth=1.0)
    for bar, val in zip(bars, values):
        ax.text(
            val * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}",
            va="center",
            fontsize=9,
            color="#233243",
        )

    ax.set_xlabel("Tokens per successful autonomous hour", fontsize=12)
    ax.set_title("Option A: Agent Token Efficiency (Lower is Better)", fontsize=15, fontweight="bold", pad=10)
    ax.invert_yaxis()
    _apply_style(fig, ax)
    ax.set_xlim(0, max(values) * 1.25)

    out = CHARTS_DIR / "token_efficiency.png"
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out


def chart_cost_efficiency(data: dict) -> Path:
    econ = data.get("agent_economics", {})
    rows = [
        row
        for row in econ.get("models", [])
        if isinstance(
            row.get("estimated_cost_scenarios", {}).get("input_70_output_30", {}).get("usd_per_autonomous_hour"),
            (int, float),
        )
    ]
    if not rows:
        return _empty_chart("cost_efficiency_70_30.png", "No estimated cost data available")

    rows = sorted(
        rows,
        key=lambda r: r["estimated_cost_scenarios"]["input_70_output_30"]["usd_per_autonomous_hour"],
    )[:10]
    models = [r["model"].replace(" (Inspect)", "") for r in rows]
    values = [r["estimated_cost_scenarios"]["input_70_output_30"]["usd_per_autonomous_hour"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    bars = ax.barh(models, values, color="#4f77b4", edgecolor="white", linewidth=1.0)
    for bar, val in zip(bars, values):
        ax.text(
            val * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"${val:.2f}",
            va="center",
            fontsize=9,
            color="#233243",
        )

    ax.set_xlabel("Estimated USD per autonomous hour", fontsize=12)
    ax.set_title("Option B: Estimated Cost per Hour (Assumed 70% Input / 30% Output)", fontsize=15, fontweight="bold", pad=10)
    ax.invert_yaxis()
    _apply_style(fig, ax)
    ax.set_xlim(0, max(values) * 1.25)

    out = CHARTS_DIR / "cost_efficiency_70_30.png"
    fig.tight_layout()
    fig.savefig(out, dpi=180, bbox_inches="tight")
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
    _init_style()
    data = _load_data()

    p1 = chart_domain_horizons(data)
    print(f"  ✓ {p1}")
    p2 = chart_success_curves(data)
    print(f"  ✓ {p2}")
    p3 = chart_model_comparison(data)
    print(f"  ✓ {p3}")
    p4 = chart_token_efficiency(data)
    print(f"  ✓ {p4}")
    p5 = chart_cost_efficiency(data)
    print(f"  ✓ {p5}")
    print("Charts generated.")


if __name__ == "__main__":
    main()
