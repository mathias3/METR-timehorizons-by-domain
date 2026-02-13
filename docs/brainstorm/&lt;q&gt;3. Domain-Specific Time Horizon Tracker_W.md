<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# <q>3. Domain-Specific Time Horizon Tracker

What it is: Break down the aggregate METR trend into domain-specific trajectories (pure coding vs. ML research vs. data analysis vs. system admin tasks).
Why it matters:

The overall trend hides important nuances

Different industries care about different task types

Current METR analysis treats all tasks equally

What you'd build:

Re-analysis of METR data segmented by domain

Separate trend lines and doubling times per domain

Identify which domains are progressing faster/slower

Interactive comparison tool

Potential findings:

Maybe coding tasks improve at 6-month doubling, but research tasks at 9 months

This would inform which jobs are most at risk and when</q> Okay, that might be interesting. Not into which jobs are being replaced, because I don't believe in that. The procedure and the direction must be done by human until there is something changes in architecture on the research approach, but dividing that by the task is great, but do we have a data or something like that, ?

Perfect! **Yes, the data exists and it's well-structured.** Here's what you have to work with:

## ✅ The Data You Need Is Available

METR has categorized their 189 tasks into **4 major domains** with **detailed subcategories**:

### 📊 Domain Breakdown (78 Task Families)

1. **Machine Learning Engineering (MLE)** - 30.8%
    - MLE training/finetuning, data science, debugging, scaffolding, data engineering
2. **Software Engineering (SWE)** - 20.5%
    - Implementation, low-level optimization, debugging, DevOps
3. **Cybersecurity** - 19.2%
    - CTF challenges, cryptography, reverse engineering, cryptocurrency exploits
4. **General Reasoning** - 29.5%
    - Common sense, algorithmic, logical, statistical reasoning

Each task has:

- **Domain classification** (one of the 4 categories above)
- **Subdomain classification** (15 specific subcategories)
- **Human baseline time estimates** (1 minute to 8+ hours)
- **Model performance data** across multiple frontier models

***

## 🎯 Refined Project Idea: Domain-Specific Time Horizon Tracker

Since the data exists with clear categorization, here's what makes this project **genuinely interesting**:

### What You Can Analyze

1. **Different progression rates by domain:**
    - Is ML engineering improving faster than cybersecurity?
    - Are reasoning tasks harder to scale than coding tasks?
    - Which domains show steeper/gentler capability curves?
2. **Task length × domain interaction:**
    - Do short MLE tasks (<15 min) behave differently than short SWE tasks?
    - Which domains have the "steepest cliff" at longer time horizons?
3. **Capability gaps by specialization:**
    - Where are models strongest/weakest relative to the overall trend?
    - Which professional specializations are most/least "at risk" of AI capability overlap?

***

## 💡 Why This Matters (Beyond Job Replacement Narrative)

I appreciate your nuance here—you're right that this shouldn't be about job replacement. Instead, focus on:

### 1. **Research \& Development Prioritization**

- Which domains need more benchmark development?
- Where should safety research focus efforts?
- Which capabilities are progressing unexpectedly fast/slow?


### 2. **AI System Design**

- Should you use different models for different domain tasks?
- Where do current architectures struggle most?
- What's the relationship between domain expertise and task length?


### 3. **Evaluation Methodology**

- Are some domains over/under-represented in benchmarks?
- Do certain domains need different evaluation approaches?
- Where are measurement gaps?


### 4. **Capability Understanding**

- Which human skills are most/least replicable by current AI?
- What does domain-specific progression tell us about AI reasoning vs. memorization?
- Where do we see surprising capability patterns?

***

## 🔧 Implementation Plan

### Phase 1: Data Access \& Exploration (Week 1)

```bash
# Get the data
git clone https://github.com/METR/eval-analysis-public
cd eval-analysis-public

# Check structure
ls reports/time-horizon-1-1/data/raw/
# You'll find: runs.jsonl, tasks.jsonl, models.jsonl
```


### Phase 2: Domain Segmentation Analysis (Weeks 2-3)

1. **Parse task metadata** - Extract domain/subdomain tags from HCAST data
2. **Map to performance data** - Join with model runs and human baselines
3. **Fit logistic curves per domain** - Separate trend lines for MLE, SWE, Cybersec, Reasoning
4. **Calculate domain-specific doubling times**
5. **Statistical testing** - Are differences significant?

### Phase 3: Build Interactive Tool (Weeks 3-4)

- **Visualizations:**
    - Overlay domain-specific curves on single plot
    - Toggle domains on/off
    - Confidence intervals per domain
    - Subdomain drill-downs (15 categories)
- **Insights panels:**
    - "Fastest improving domain: [X] (doubling every [Y] months)"
    - "Most challenging domain for AI: [Z]"
    - Heatmap: model performance × domain × time horizon


### Phase 4: Write-up \& Release (Week 5)

- Technical blog post with findings
- Open-source repo with analysis code
- Interactive demo deployed (Streamlit Cloud free tier)

***

## 📈 Potential Findings (Hypotheses to Test)

1. **MLE tasks might improve faster** - More training data, better memorization
2. **Cybersecurity might have steeper curves** - Requires novel creative problem-solving
3. **General reasoning might plateau earlier** - Abstract reasoning harder to scale
4. **Software engineering might be most predictable** - Well-defined problems, clear scoring

These are just hypotheses—**your analysis will reveal the truth**.

***

## 🚀 Next Steps

Want to proceed with this? I can help you:

1. **Examine the actual data structure** from their GitHub repo
2. **Write the data parsing pipeline** to extract domain labels
3. **Build the curve fitting code** for per-domain analysis
4. **Design the interactive visualization** layout

Should we start by pulling down their data and seeing exactly what's in `runs.jsonl` and `tasks.jsonl`?
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/METR/public-tasks

[^2]: https://www.scribd.com/document/893323837/2503-14499v2-10

[^3]: https://github.com/METR/task-template

[^4]: https://github.com/METR/task-standard

[^5]: https://arxiv.org/html/2503.17354v1

[^6]: https://metr.substack.com/p/2024-02-29-metr-task-standard

[^7]: https://arxiv.org/html/2503.14499v1

[^8]: https://neurips.cc/virtual/2025/poster/119302

[^9]: https://www.mete.is/crow/tasks/

[^10]: https://github.com/METR/task-standard/blob/main/README.md

[^11]: https://openreview.net/forum?id=CGNJL6CeV0

[^12]: https://github.com/METR/public-tasks/labels

[^13]: https://metr.org/hcast.pdf

[^14]: https://rexbench.com

[^15]: https://taskdev.metr.org/documentation/

