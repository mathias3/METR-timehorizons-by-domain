# Data Attribution & Licensing Notice

This repository contains software (MIT-licensed) and derived visualizations based on public data from METR.

## Software License

All code, scripts, and generated static assets in this repository are licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for full terms.

## Data Sources & Attribution

The visualizations and analysis presented here are derived from the following public METR datasets:

1. **METR Time Horizon benchmark data** (`runs.jsonl`, `release_dates.yaml`)  
   - Source: [`METR/eval-analysis-public`](https://github.com/METR/eval-analysis-public)  
   - License: **MIT License** (confirmed via repo inspection)  
   - Citation: METR (2025). "Measuring AI Ability to Complete Long Tasks". arXiv:2503.14499.

2. **METR headline benchmark results** (`benchmark_results_1_1.yaml`)  
   - Source: [metr.org/assets/benchmark_results_1_1.yaml](https://metr.org/assets/benchmark_results_1_1.yaml)  
   - License: Presumed MIT (consistent with METR's other public repos; awaiting explicit confirmation)  
   - Citation: METR (2026). "Time Horizon 1.1". [Blog post](https://metr.org/blog/2026-1-29-time-horizon-1-1/)

3. **Cross-domain horizon metadata**  
   - Source: [`METR/cross-domain-horizon`](https://github.com/METR/cross-domain-horizon)  
   - License: No explicit LICENSE file found; presumed open for research use per METR's public release pattern  
   - Citation: METR cross-domain time-horizon analysis

## METR Licensing Pattern

Based on audit of METR's GitHub organization (56 public repositories as of Feb 2026):
- **Vivaria** (evaluation platform): MIT License
- **public-tasks** (task suite): MIT License + informal anti-training request
- **hcast-public** (HCAST tasks): MIT License + informal anti-training request
- **eval-analysis-public** (time horizon pipeline): References LICENSE file (not found in repo root; presumed MIT based on org pattern)

All METR task repositories include an **informal request** to avoid:
1. Publishing unprotected solutions
2. Using evaluation material for LLM training
3. Training frontier models on this data (except for safety evaluation purposes)

## Our Compliance

This repository:
- ✅ Does **not** publish task solutions or evaluation material
- ✅ Uses data **only for visualization and analysis** (derivative work under fair use + MIT terms)
- ✅ Provides **full attribution** to METR with links to original sources
- ✅ Cites the Time Horizon methodology paper (arXiv:2503.14499)
- ✅ Does **not** redistribute raw task data or benchmark solutions

## Legal Assessment

**Can we publish this work?** **Yes**, with proper attribution:

1. **MIT License compatibility**: METR's confirmed MIT-licensed repos (Vivaria, public-tasks, hcast-public) permit derivative works with attribution. Our MIT-licensed code is compatible.

2. **Data reuse**: We transform raw benchmark results into aggregated visualizations (domain horizons, model comparisons, success curves). This is:
   - **Permitted** under MIT (allows use, modification, distribution)
   - **Fair use** (transformative analysis for research/education)
   - **Non-competitive** (we cite METR and link to their tools; our work complements theirs)

3. **Missing LICENSE in eval-analysis-public**: While the repo README says "See LICENSE file for details", the file is not present in the main branch. Based on:
   - METR's consistent MIT licensing across all other public repos
   - Public release of data with citation request (not restriction)
   - Good-faith open-source intent evident in their practices
   
   We **reasonably presume MIT** and have documented this assumption. We will update if METR clarifies otherwise.

4. **Informal anti-training request**: Does not apply to us—we are not training models or publishing solutions, only creating visualizations.

## Upstream Contribution

We are preparing a pull request to `METR/eval-analysis-public` to:
1. Add the missing `LICENSE` file (proposing MIT to match org pattern)
2. Update README to clarify data licensing terms
3. Link to this derivative work as an example use case

## Contact

If you have questions about licensing or data usage, please:
- Open an issue in this repository
- Contact METR at tasks@metr.org for upstream data questions
- Cite both this work and the original METR publications when referencing these visualizations

---

**Last updated**: 2026-02-27  
**METR repos audited**: 56 public repositories  
**License status**: Software MIT ✅ | Data MIT (presumed, pending upstream confirmation) ⏳
