<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Ok, for a long time I didn't do any open source projects and as I'm a machine learning engineer and I'm connected to things like agents, LLMs and other things, I was wondering what can I do to refresh my skill of doing some open source projects and other stuff. I was thinking for at the beginning to do something with this table or tests or assessments of models, no idea what to do, I want to do something and it would be great to get some ideas from you what can be done, what can be best, be in a matter substancial .Something productive, some content that actually will give something to the public or to the people who might be interested about something around that, some insight, something not hyping but showing anything interesting which is not shown by the data existing there. Showing data in other way, no idea what that should be but I'm just thinking about ideas here for now and giving the quality content for people. here is the data  [https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)

Based on my analysis of the METR benchmark data and the broader AI agent evaluation landscape, I've identified several **high-impact open-source project ideas** that would provide genuine value to the ML community. Let me break these down from most to least substantial:

## 🎯 Top Tier Projects (High Impact)

### 1. **Interactive Time Horizon Explorer \& Forecasting Tool**

**What it is:** A web-based interactive dashboard that lets researchers and practitioners explore the METR time horizon data with custom forecasting scenarios.

**Why it matters:**

- METR shows AI capabilities doubling every 7 months, but their analysis is static
- No tool exists to explore "what-if" scenarios (e.g., "what if the trend slows to 12-month doubling?")
- Critical for AI safety researchers and policy makers to understand timelines

**Key features:**

- Interactive logistic curve fitting with confidence intervals
- Ability to filter by task types (software vs. ML research vs. general)
- Custom forecasting with adjustable parameters (doubling time, trend breaks)
- Comparison tool: overlay multiple models' trajectories
- Export publication-ready plots and data tables

**Technical stack:** Python (Plotly/Dash or Streamlit), pandas, scipy for curve fitting, the METR dataset from their GitHub

***

### 2. **Cross-Benchmark Task Duration Dataset \& Analysis**

**What it is:** Aggregate human completion time estimates across multiple benchmarks (METR, SWE-Bench Verified, AstaBench) into a unified dataset with analysis tools.

**Why it matters:**

- Different benchmarks measure similar things but lack standardization
- No unified view of how task complexity relates across datasets
- Researchers can't easily compare apples-to-apples

**Key contributions:**

- Normalized dataset mapping tasks to human completion times
- Statistical analysis of task difficulty distributions
- Identify gaps: what task durations are under-represented?
- Correlation analysis: which task types predict model performance best?

**Novel insights you could uncover:**

- Are 10-minute coding tasks fundamentally different from 10-minute ML research tasks for AI?
- Which benchmarks have the most "realistic" task distributions?
- Where should new benchmarks focus to fill gaps?

***

### 3. **Domain-Specific Time Horizon Tracker**

**What it is:** Break down the aggregate METR trend into domain-specific trajectories (pure coding vs. ML research vs. data analysis vs. system admin tasks).

**Why it matters:**

- The overall trend hides important nuances
- Different industries care about different task types
- Current METR analysis treats all tasks equally

**What you'd build:**

- Re-analysis of METR data segmented by domain
- Separate trend lines and doubling times per domain
- Identify which domains are progressing faster/slower
- Interactive comparison tool

**Potential findings:**

- Maybe coding tasks improve at 6-month doubling, but research tasks at 9 months
- This would inform which jobs are most at risk and when

***

## 🔬 Mid Tier Projects (Solid Contributions)

### 4. **Benchmark Task Complexity Classifier**

**What it is:** ML model that predicts human completion time for a task based on its description and characteristics.

**Why useful:**

- New benchmarks need human timing data (expensive to collect)
- Could bootstrap new evaluations faster
- Helps identify if a benchmark is "too easy" or "too hard" before running expensive evals

**Approach:**

- Train on METR + SWE-Bench Verified data (you have both task descriptions and human times)
- Features: task description embeddings, code complexity metrics, required tool counts
- Output: predicted human completion time + confidence interval

***

### 5. **LLM Performance Decay Analyzer**

**What it is:** Tool to identify at what task length each model's performance "falls off a cliff."

**The insight:**

- METR shows logistic curves, but the steepness varies by model
- Some models might be great at 5-min tasks but terrible at 20-min tasks
- Others might have gentler decline

**What you'd create:**

- Metric for "performance cliff steepness"
- Ranking of models by robustness to task length
- Visualization of failure modes at different time scales
- Practical guidance: "Use Model X for tasks under N hours"

***

## 🛠️ Practical Tools (Community Value)

### 6. **Agent Evaluation Cost Calculator**

**What it is:** Tool to estimate the cost and time required to evaluate a new AI agent on various benchmarks.

**Why needed:**

- Running evals is expensive (API costs, compute time)
- Researchers need to budget before starting
- No existing tool provides estimates

**Features:**

- Input: model name, benchmark choice, number of runs
- Output: estimated cost, time, token usage
- Based on empirical data from METR's published runs
- Helps smaller labs plan evaluations

***

### 7. **Benchmark Task Difficulty Visualizer**

**What it is:** Generate publication-ready visualizations comparing task difficulty distributions across benchmarks.

**Value:**

- Helps researchers choose appropriate benchmarks
- Reveals biases in existing benchmarks
- Beautiful, interactive charts for papers/blogs

**What makes it different:**

- Focus on making complex data accessible to non-specialists
- One-click generation of comparison plots
- Export formats for papers (PDF/SVG) and web (interactive HTML)

***

## 💡 My Top Recommendation

I'd suggest **Project \#1 (Interactive Time Horizon Explorer)** or **Project \#2 (Cross-Benchmark Dataset)** because:

1. **High utility:** Researchers, safety orgs, and policymakers need these tools NOW
2. **Data is available:** METR open-sourced their data, SWE-Bench is public
3. **Novel insights:** Current published work is static; interactive exploration enables new discoveries
4. **Clear scope:** Can ship an MVP in 2-4 weeks, then iterate
5. **Visibility:** METR, Anthropic, OpenAI researchers will notice and cite this work
6. **Future-proof:** As new models release, the tool remains valuable (just add new data points)

***

## 🚀 Getting Started (Practical Next Steps)

1. **Clone the METR dataset**: `git clone https://github.com/METR/eval-analysis-public`
2. **Explore the data structure**: Check `reports/time-horizon-1-1/data/raw/runs.jsonl`
3. **Replicate their basic plots**: Start by reproducing their core figures
4. **Add one novel view**: Maybe task duration vs. model cost, or domain-specific breakdowns
5. **Build interactive version**: Convert static plots to Plotly/Streamlit
6. **Share early**: Post progress on Twitter/LinkedIn, tag METR researchers
7. **Write a technical blog post**: Explain your methodology and findings
8. **Submit to relevant communities**: LessWrong, AI Alignment Forum, r/MachineLearning

***

## 📊 What Makes These Projects "Substantial"?

- **Original analysis**, not just data visualization
- **Actionable insights** for practitioners
- **Fills gaps** in current tooling/understanding
- **Open data + open code** = maximum community value
- **Citable work** that advances the field

Would you like me to deep-dive into the implementation plan for any of these? I can help you outline the data pipeline, technical architecture, or specific analyses to run.
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/METR/eval-analysis-public

[^2]: https://openai.com/index/introducing-swe-bench-verified/

[^3]: https://github.com/rungalileo/agent-leaderboard

[^4]: https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

[^5]: https://epoch.ai/benchmarks/swe-bench-verified

[^6]: https://datatalks.club/blog/open-source-free-ai-agent-evaluation-tools.html

[^7]: https://www.mete.is/crow/tasks/

[^8]: https://www.verdent.ai/blog/swe-bench-verified-technical-report

[^9]: https://allenai.org/blog/astabench

[^10]: https://github.com/METR/public-tasks

[^11]: https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified

[^12]: https://o-mega.ai/articles/the-best-ai-agent-evals-and-benchmarks-full-2025-guide

[^13]: https://epoch.ai/benchmarks/metr-time-horizons

[^14]: https://www.swebench.com

[^15]: https://tessl.io/blog/8-benchmarks-shaping-the-next-generation-of-ai-agents/

