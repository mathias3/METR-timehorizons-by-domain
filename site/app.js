async function loadData() {
  const response = await fetch("./data.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Cannot load data.json (${response.status})`);
  }
  return response.json();
}

const DOMAIN_LABELS = {
  cybersecurity: "Cybersecurity",
  ml_research: "ML / AI Research",
  software_engineering: "Software Engineering",
  data_analysis: "Data & Research",
  reasoning: "Reasoning",
  unknown: "General / Other",
};

const DOMAIN_COLORS = {
  cybersecurity: "#cc5c67",
  ml_research: "#4f78b8",
  software_engineering: "#379f8c",
  data_analysis: "#d09256",
  reasoning: "#8d74b7",
  unknown: "#708090",
};

const STORY_CAPTIONS = [
  "All domains shown together.",
  "Highlighting short-duration region where most models saturate.",
  "Focusing on 32-512 minute interval where failures accelerate.",
  "Comparing domain-average curves for separation.",
  "Showing top frontier models only.",
];

const APP_STATE = {
  data: null,
  activeDomains: new Set(),
  splitKey: null,
  scrollerReady: false,
  scroller: null,
  storyStep: 0,
};

function labelDomain(domain) {
  return DOMAIN_LABELS[domain] || domain;
}

function colorDomain(domain) {
  return DOMAIN_COLORS[domain] || "#61758a";
}

function shortModelName(name) {
  return String(name || "").replace(" (Inspect)", "");
}

function safeNumber(value, fallback = null) {
  return Number.isFinite(value) ? value : fallback;
}

function toMinutesLabel(minutes) {
  if (!Number.isFinite(minutes)) return "n/a";
  if (minutes >= 60) return `${(minutes / 60).toFixed(1)} h`;
  if (minutes >= 1) return `${minutes.toFixed(1)} min`;
  return `${(minutes * 60).toFixed(0)} s`;
}

function getContainerWidth(id, fallback) {
  const node = document.getElementById(id);
  return Math.max(node?.clientWidth || fallback, 320);
}

function initSvg(containerId, width, height) {
  const host = d3.select(`#${containerId}`);
  host.selectAll("*").remove();
  return host
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet");
}

function showTooltip(event, html) {
  const tip = document.getElementById("tooltip");
  tip.innerHTML = html;
  tip.classList.add("show");
  tip.style.left = `${event.clientX + 12}px`;
  tip.style.top = `${event.clientY + 12}px`;
}

function moveTooltip(event) {
  const tip = document.getElementById("tooltip");
  tip.style.left = `${event.clientX + 12}px`;
  tip.style.top = `${event.clientY + 12}px`;
}

function hideTooltip() {
  document.getElementById("tooltip").classList.remove("show");
}

function prepareBubbleRows(data) {
  const curveIndex = new Map(data.curves.map((row) => [`${row.model}__${row.domain}`, row]));

  function successNear60(points) {
    if (!points || !points.length) return null;
    let best = points[0];
    let bestDist = Math.abs(points[0].minutes - 60);
    points.forEach((p) => {
      const dist = Math.abs(p.minutes - 60);
      if (dist < bestDist) {
        best = p;
        bestDist = dist;
      }
    });
    return safeNumber(best.success_smoothed ?? best.success, null);
  }

  return data.model_domain
    .map((row) => {
      const curve = curveIndex.get(`${row.model}__${row.domain}`);
      return {
        ...row,
        horizon_minutes: safeNumber(row.horizon_minutes, 0),
        points: safeNumber(row.n_points, 0),
        success60: successNear60(curve?.points || []),
      };
    })
    .filter((row) => row.horizon_minutes > 0 && row.success60 !== null);
}

function renderDomainFilter(domains, active, onChange) {
  const host = document.getElementById("domain-filter");
  host.innerHTML = "";

  const all = document.createElement("button");
  all.className = `chip ${active.size === 0 ? "active" : ""}`;
  all.type = "button";
  all.textContent = "All domains";
  all.addEventListener("click", () => onChange(new Set()));
  host.appendChild(all);

  domains.forEach((domain) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `chip ${active.has(domain) ? "active" : ""}`;
    btn.textContent = labelDomain(domain);
    btn.addEventListener("click", () => {
      const next = new Set(active);
      if (next.has(domain)) next.delete(domain);
      else next.add(domain);
      onChange(next);
    });
    host.appendChild(btn);
  });
}

function renderBubbleChart(data, bubbleRows, activeDomains) {
  const width = getContainerWidth("bubble-chart", 860);
  const height = 480;
  const margin = { top: 16, right: 24, bottom: 52, left: 72 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("bubble-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const visible =
    activeDomains.size === 0
      ? bubbleRows
      : bubbleRows.filter((row) => activeDomains.has(row.domain));

  const x = d3
    .scaleLog()
    .domain([0.5, d3.max(bubbleRows, (d) => d.horizon_minutes) * 1.15])
    .range([0, innerW]);

  const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  const r = d3
    .scaleSqrt()
    .domain([0, d3.max(bubbleRows, (d) => d.points)])
    .range([4, 28]);

  g.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(6, "~s"));

  g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6).tickFormat((d) => `${d}%`));

  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#1c344a")
    .text("Autonomy horizon (minutes, log scale)");

  g.append("text")
    .attr("x", -innerH / 2)
    .attr("y", -48)
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("fill", "#1c344a")
    .text("Success probability near 60 min");

  g.append("line")
    .attr("x1", 0)
    .attr("x2", innerW)
    .attr("y1", y(50))
    .attr("y2", y(50))
    .attr("stroke", "#90a8bf")
    .attr("stroke-dasharray", "5,5")
    .attr("stroke-width", 1.2);

  g.append("text")
    .attr("x", innerW - 2)
    .attr("y", y(50) - 7)
    .attr("text-anchor", "end")
    .attr("fill", "#5c7389")
    .style("font-size", "11px")
    .text("50% threshold");

  g.selectAll("circle.bubble")
    .data(visible, (d) => `${d.model}-${d.domain}`)
    .join("circle")
    .attr("class", "bubble")
    .attr("cx", (d) => x(d.horizon_minutes))
    .attr("cy", (d) => y(d.success60 * 100))
    .attr("r", 0)
    .attr("fill", (d) => colorDomain(d.domain))
    .attr("fill-opacity", 0.72)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.2)
    .on("mouseenter", (event, d) => {
      showTooltip(
        event,
        `<strong>${shortModelName(d.model)}</strong><br>${labelDomain(d.domain)}<br>Horizon: ${toMinutesLabel(
          d.horizon_minutes
        )}<br>Success near 60m: ${(d.success60 * 100).toFixed(1)}%<br>Points: ${d.points}`
      );
    })
    .on("mousemove", moveTooltip)
    .on("mouseleave", hideTooltip)
    .transition()
    .duration(550)
    .attr("r", (d) => r(d.points));
}

function renderStoryChart(data, step = 0) {
  const width = getContainerWidth("story-chart", 860);
  const height = 400;
  const margin = { top: 20, right: 22, bottom: 54, left: 66 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("story-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const byDomain = d3.group(data.curves, (d) => d.domain);
  const domainSeries = Array.from(byDomain, ([domain, rows]) => {
    const points = d3
      .rollups(
        rows.flatMap((r) => r.points),
        (vals) => d3.mean(vals, (v) => safeNumber(v.success_smoothed ?? v.success, 0)),
        (d) => d.minutes
      )
      .map(([minutes, success]) => ({ minutes: +minutes, success: success * 100 }))
      .sort((a, b) => a.minutes - b.minutes)
      .filter((d) => d.minutes > 0);
    return { domain, points };
  });

  const x = d3.scaleLog().domain([0.02, 600]).range([0, innerW]);
  const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  g.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(9, "~s"));

  g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6).tickFormat((d) => `${d}%`));

  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 42)
    .attr("text-anchor", "middle")
    .attr("fill", "#1c344a")
    .text("Task duration (minutes, log scale)");

  g.append("text")
    .attr("x", -innerH / 2)
    .attr("y", -44)
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("fill", "#1c344a")
    .text("Success rate");

  const line = d3
    .line()
    .curve(d3.curveCatmullRom.alpha(0.4))
    .x((d) => x(d.minutes))
    .y((d) => y(d.success));

  const lines = g
    .selectAll("path.domain-line")
    .data(domainSeries)
    .join("path")
    .attr("class", "domain-line")
    .attr("d", (d) => line(d.points))
    .attr("fill", "none")
    .attr("stroke", (d) => colorDomain(d.domain))
    .attr("stroke-width", 2.4)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.92);

  if (step === 1) {
    g.append("rect")
      .attr("x", x(0.02))
      .attr("y", 0)
      .attr("width", x(8) - x(0.02))
      .attr("height", innerH)
      .attr("fill", "#dcecff")
      .attr("opacity", 0.35);
  }

  if (step === 2) {
    g.append("rect")
      .attr("x", x(32))
      .attr("y", 0)
      .attr("width", x(512) - x(32))
      .attr("height", innerH)
      .attr("fill", "#ffe5df")
      .attr("opacity", 0.35);
  }

  if (step === 4) {
    const topModels = new Set(
      [...data.model_domain]
        .sort((a, b) => b.horizon_minutes - a.horizon_minutes)
        .slice(0, 3)
        .map((d) => d.model)
    );
    lines.attr("opacity", 0.18);

    const topCurves = data.curves.filter((row) => topModels.has(row.model));
    g.selectAll("path.frontier")
      .data(topCurves)
      .join("path")
      .attr("class", "frontier")
      .attr("d", (d) => line(d.points.map((p) => ({ minutes: p.minutes, success: p.success * 100 }))))
      .attr("fill", "none")
      .attr("stroke", (d) => colorDomain(d.domain))
      .attr("stroke-width", 3)
      .attr("opacity", 0.9);
  }

  const legend = g.append("g").attr("transform", `translate(${innerW - 140},6)`);
  const domains = domainSeries.map((d) => d.domain);
  domains.forEach((domain, i) => {
    legend
      .append("line")
      .attr("x1", 0)
      .attr("x2", 16)
      .attr("y1", i * 16)
      .attr("y2", i * 16)
      .attr("stroke", colorDomain(domain))
      .attr("stroke-width", 3);
    legend
      .append("text")
      .attr("x", 20)
      .attr("y", i * 16 + 4)
      .style("font-size", "11px")
      .attr("fill", "#25394d")
      .text(labelDomain(domain));
  });
}

function renderDomainLollipop(data) {
  const rows = [...data.domain_horizons].sort((a, b) => b.horizon_p50_minutes - a.horizon_p50_minutes);
  const width = getContainerWidth("domain-chart", 980);
  const height = 390;
  const margin = { top: 20, right: 42, bottom: 34, left: 195 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("domain-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([0, d3.max(rows, (d) => d.horizon_ci_high_minutes) * 1.08]).range([0, innerW]);
  const y = d3
    .scaleBand()
    .domain(rows.map((d) => d.domain))
    .range([0, innerH])
    .padding(0.34);

  g.append("g").attr("class", "axis").call(d3.axisLeft(y).tickFormat((d) => labelDomain(d)));
  g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(7));

  const line = g
    .selectAll("line.lollipop")
    .data(rows)
    .join("line")
    .attr("class", "lollipop")
    .attr("x1", 0)
    .attr("x2", 0)
    .attr("y1", (d) => y(d.domain) + y.bandwidth() / 2)
    .attr("y2", (d) => y(d.domain) + y.bandwidth() / 2)
    .attr("stroke", "#b0c2d4")
    .attr("stroke-width", 3);

  line.transition().duration(700).attr("x2", (d) => x(d.horizon_p50_minutes));

  g.selectAll("line.ci")
    .data(rows)
    .join("line")
    .attr("class", "ci")
    .attr("x1", (d) => x(d.horizon_ci_low_minutes))
    .attr("x2", (d) => x(d.horizon_ci_high_minutes))
    .attr("y1", (d) => y(d.domain) + y.bandwidth() / 2)
    .attr("y2", (d) => y(d.domain) + y.bandwidth() / 2)
    .attr("stroke", "#5f7286")
    .attr("stroke-width", 1.6)
    .attr("stroke-opacity", 0.8);

  g.selectAll("circle.dot")
    .data(rows)
    .join("circle")
    .attr("class", "dot")
    .attr("cx", (d) => x(d.horizon_p50_minutes))
    .attr("cy", (d) => y(d.domain) + y.bandwidth() / 2)
    .attr("r", 6.5)
    .attr("fill", (d) => colorDomain(d.domain))
    .on("mouseenter", (event, d) => {
      showTooltip(
        event,
        `<strong>${labelDomain(d.domain)}</strong><br>P50 horizon: ${toMinutesLabel(
          d.horizon_p50_minutes
        )}<br>CI: ${toMinutesLabel(d.horizon_ci_low_minutes)} - ${toMinutesLabel(d.horizon_ci_high_minutes)}`
      );
    })
    .on("mousemove", moveTooltip)
    .on("mouseleave", hideTooltip);
}

function renderHeatmap(data) {
  const rows = data.model_domain.filter((r) => r.model.toLowerCase() !== "human");
  const topModels = [...rows]
    .sort((a, b) => b.horizon_minutes - a.horizon_minutes)
    .map((r) => r.model)
    .filter((model, idx, arr) => arr.indexOf(model) === idx)
    .slice(0, 12);

  const domains = [...new Set(rows.map((r) => r.domain))];
  const gridData = [];
  topModels.forEach((model) => {
    domains.forEach((domain) => {
      const match = rows.find((r) => r.model === model && r.domain === domain);
      gridData.push({
        model,
        domain,
        value: safeNumber(match?.horizon_minutes, 0),
      });
    });
  });

  const width = getContainerWidth("heatmap-chart", 980);
  const height = 520;
  const margin = { top: 26, right: 20, bottom: 66, left: 240 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("heatmap-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand().domain(domains).range([0, innerW]).padding(0.08);
  const y = d3.scaleBand().domain(topModels).range([0, innerH]).padding(0.08);

  const color = d3
    .scaleSequential()
    .domain([0, d3.max(gridData, (d) => d.value)])
    .interpolator(d3.interpolateYlGnBu);

  g.selectAll("rect.cell")
    .data(gridData)
    .join("rect")
    .attr("class", "cell")
    .attr("x", (d) => x(d.domain))
    .attr("y", (d) => y(d.model))
    .attr("width", x.bandwidth())
    .attr("height", y.bandwidth())
    .attr("rx", 4)
    .attr("fill", (d) => color(d.value))
    .on("mouseenter", (event, d) => {
      showTooltip(
        event,
        `<strong>${shortModelName(d.model)}</strong><br>${labelDomain(d.domain)}<br>Horizon: ${toMinutesLabel(
          d.value
        )}`
      );
    })
    .on("mousemove", moveTooltip)
    .on("mouseleave", hideTooltip);

  g.append("g")
    .attr("class", "axis")
    .call(d3.axisLeft(y).tickFormat((d) => shortModelName(d).slice(0, 26)));

  g.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).tickFormat((d) => labelDomain(d)))
    .selectAll("text")
    .attr("transform", "rotate(-20)")
    .style("text-anchor", "end");
}

function renderTokenDotPlot(data) {
  const rows = (data.agent_economics?.models || [])
    .filter((m) => Number.isFinite(m.tokens_per_success_hour))
    .sort((a, b) => a.tokens_per_success_hour - b.tokens_per_success_hour)
    .slice(0, 12);

  const width = getContainerWidth("token-efficiency-chart", 640);
  const height = 390;
  const margin = { top: 20, right: 28, bottom: 40, left: 220 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("token-efficiency-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain([0, d3.max(rows, (d) => d.tokens_per_success_hour) * 1.1])
    .range([0, innerW]);

  const y = d3
    .scaleBand()
    .domain(rows.map((d) => d.model))
    .range([0, innerH])
    .padding(0.42);

  const color = d3
    .scaleLinear()
    .domain(d3.extent(rows, (d) => d.tokens_per_success_hour))
    .range(["#2f9b8d", "#cb6a60"]);

  g.append("g").attr("class", "axis").call(d3.axisLeft(y).tickFormat((d) => shortModelName(d).slice(0, 25)));
  g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(6));

  g.selectAll("line.stem")
    .data(rows)
    .join("line")
    .attr("x1", 0)
    .attr("x2", (d) => x(d.tokens_per_success_hour))
    .attr("y1", (d) => y(d.model) + y.bandwidth() / 2)
    .attr("y2", (d) => y(d.model) + y.bandwidth() / 2)
    .attr("stroke", "#bdccdc")
    .attr("stroke-width", 2.4);

  g.selectAll("circle.dot")
    .data(rows)
    .join("circle")
    .attr("cx", (d) => x(d.tokens_per_success_hour))
    .attr("cy", (d) => y(d.model) + y.bandwidth() / 2)
    .attr("r", 7)
    .attr("fill", (d) => color(d.tokens_per_success_hour))
    .on("mouseenter", (event, d) => {
      showTooltip(
        event,
        `<strong>${shortModelName(d.model)}</strong><br>${d.tokens_per_success_hour.toLocaleString()} tokens / success hour`
      );
    })
    .on("mousemove", moveTooltip)
    .on("mouseleave", hideTooltip);
}

function paretoFrontier(rows) {
  const sorted = [...rows].sort((a, b) => a.tokens - b.tokens);
  const frontier = [];
  let best = Infinity;
  sorted.forEach((row) => {
    if (row.usd <= best) {
      frontier.push(row);
      best = row.usd;
    }
  });
  return frontier;
}

function renderCostScatter(data, presetKey) {
  const rows = (data.agent_economics?.models || [])
    .map((m) => ({
      model: m.model,
      tokens: m.tokens_per_success_hour,
      usd: m.estimated_cost_scenarios?.[presetKey]?.usd_per_autonomous_hour,
      runs: m.runs_success || 0,
    }))
    .filter((d) => Number.isFinite(d.tokens) && Number.isFinite(d.usd));

  const width = getContainerWidth("cost-efficiency-chart", 640);
  const height = 390;
  const margin = { top: 16, right: 16, bottom: 48, left: 66 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const svg = initSvg("cost-efficiency-chart", width, height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain([0, d3.max(rows, (d) => d.tokens) * 1.1])
    .range([0, innerW]);
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(rows, (d) => d.usd) * 1.12])
    .range([innerH, 0]);
  const r = d3.scaleSqrt().domain([0, d3.max(rows, (d) => d.runs)]).range([5, 16]);

  g.append("g").attr("class", "axis").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(6));
  g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6));

  g.append("text")
    .attr("x", innerW / 2)
    .attr("y", innerH + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#1c344a")
    .text("Tokens per successful autonomous hour");

  g.append("text")
    .attr("x", -innerH / 2)
    .attr("y", -44)
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("fill", "#1c344a")
    .text("Estimated USD per autonomous hour");

  g.selectAll("circle.cost")
    .data(rows)
    .join("circle")
    .attr("cx", (d) => x(d.tokens))
    .attr("cy", (d) => y(d.usd))
    .attr("r", (d) => r(d.runs))
    .attr("fill", "#2f7ea5")
    .attr("fill-opacity", 0.62)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.1)
    .on("mouseenter", (event, d) => {
      showTooltip(
        event,
        `<strong>${shortModelName(d.model)}</strong><br>${d.tokens.toLocaleString()} tokens/success hr<br>$${d.usd.toFixed(
          2
        )} per autonomous hr`
      );
    })
    .on("mousemove", moveTooltip)
    .on("mouseleave", hideTooltip);

  const frontier = paretoFrontier(rows);
  const line = d3
    .line()
    .x((d) => x(d.tokens))
    .y((d) => y(d.usd));

  g.append("path")
    .datum(frontier)
    .attr("fill", "none")
    .attr("stroke", "#c1545e")
    .attr("stroke-width", 2.2)
    .attr("stroke-dasharray", "4,4")
    .attr("d", line);
}

function setupSplitSelector(data) {
  const splitPresets = data.agent_economics?.split_presets || {};
  const keys = Object.keys(splitPresets);
  const select = document.getElementById("split-select");
  const note = document.getElementById("split-note");
  if (!select.dataset.bound) {
    select.innerHTML = "";
    keys.forEach((key) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = splitPresets[key].label || key;
      select.appendChild(option);
    });

    const initialKey = keys.includes("input_70_output_30") ? "input_70_output_30" : keys[0];
    APP_STATE.splitKey = APP_STATE.splitKey || initialKey;
    select.dataset.bound = "1";

    select.addEventListener("change", () => {
      APP_STATE.splitKey = select.value;
      renderAll();
    });
  }

  if (!APP_STATE.splitKey || !splitPresets[APP_STATE.splitKey]) {
    APP_STATE.splitKey = keys.includes("input_70_output_30") ? "input_70_output_30" : keys[0];
  }
  select.value = APP_STATE.splitKey;

  const preset = splitPresets[APP_STATE.splitKey];
  if (!preset) {
    note.textContent = "";
  } else {
    note.textContent = `Assumption: ${Math.round(preset.input_share * 100)}% input / ${Math.round(
      preset.output_share * 100
    )}% output. Data has total tokens only.`;
  }
}

function renderTable(data) {
  const tbody = document.querySelector("#records-table tbody");
  tbody.innerHTML = "";
  data.table_rows.slice(0, 150).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.benchmark}</td>
      <td>${labelDomain(row.domain)}</td>
      <td>${shortModelName(row.model)}</td>
      <td>${row.release_date || ""}</td>
      <td>${Number(row.human_minutes || 0).toFixed(2)}</td>
      <td>${Number(row.score || 0).toFixed(3)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function setupStoryScroller(data) {
  if (APP_STATE.scrollerReady) {
    return;
  }
  const steps = Array.from(document.querySelectorAll(".step"));
  function activate(stepIndex) {
    APP_STATE.storyStep = stepIndex;
    steps.forEach((el, idx) => {
      el.classList.toggle("is-active", idx === stepIndex);
    });
    document.getElementById("story-caption").textContent = STORY_CAPTIONS[stepIndex] || STORY_CAPTIONS[0];
    renderStoryChart(data, stepIndex);
  }

  activate(0);

  if (!window.scrollama || window.innerWidth < 900) {
    APP_STATE.scrollerReady = true;
    return;
  }

  APP_STATE.scroller = window.scrollama();
  APP_STATE.scroller
    .setup({ step: ".step", offset: 0.5, progress: false })
    .onStepEnter(({ element }) => {
      const step = Number(element.getAttribute("data-step") || 0);
      activate(step);
    });

  APP_STATE.scrollerReady = true;
}

function renderAll() {
  const { data, activeDomains } = APP_STATE;
  if (!data) return;
  const bubbleRows = prepareBubbleRows(data);
  const domains = [...new Set(bubbleRows.map((d) => d.domain))].sort();

  renderDomainFilter(domains, activeDomains, (nextSet) => {
    APP_STATE.activeDomains = nextSet;
    renderAll();
  });
  renderBubbleChart(data, bubbleRows, activeDomains);
  renderDomainLollipop(data);
  renderHeatmap(data);
  renderTokenDotPlot(data);
  setupSplitSelector(data);
  renderCostScatter(data, APP_STATE.splitKey);
  renderStoryChart(data, APP_STATE.storyStep);
  renderTable(data);
  setupStoryScroller(data);
}

async function init() {
  try {
    const data = await loadData();
    APP_STATE.data = data;
    APP_STATE.activeDomains = new Set();
    renderAll();
    document.getElementById("generated-at").textContent = `Generated at: ${data.generated_at}`;

    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        renderAll();
        if (APP_STATE.scroller && typeof APP_STATE.scroller.resize === "function") {
          APP_STATE.scroller.resize();
        }
      }, 220);
    });
  } catch (error) {
    console.error(error);
    document.body.innerHTML += `<p style="padding:1rem;color:#991b1b">${error.message}</p>`;
  }
}

window.addEventListener("DOMContentLoaded", init);
