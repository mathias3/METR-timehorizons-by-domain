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
  cybersecurity: "#c85663",
  ml_research: "#4f77b4",
  software_engineering: "#3f9e8b",
  data_analysis: "#d4955e",
  reasoning: "#9a7fb8",
  unknown: "#7a7f87",
};

const CHART_CONFIG = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoscale", "toImage"],
};

function labelDomain(domain) {
  return DOMAIN_LABELS[domain] || domain;
}

function colorDomain(domain) {
  return DOMAIN_COLORS[domain] || "#61758a";
}

function axisBase() {
  return {
    showline: true,
    linecolor: "#a9b7c6",
    linewidth: 1,
    gridcolor: "#e7edf4",
    gridwidth: 1,
    tickfont: { size: 12, color: "#233243" },
    titlefont: { size: 14, color: "#233243" },
    zeroline: false,
  };
}

function layoutBase() {
  return {
    template: "simple_white",
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    margin: { t: 40, r: 20, b: 70, l: 70 },
    font: {
      family: "IBM Plex Sans, Source Sans 3, Segoe UI, sans-serif",
      size: 13,
      color: "#233243",
    },
    legend: {
      bgcolor: "rgba(255,255,255,0.9)",
      bordercolor: "#d9e2ec",
      borderwidth: 1,
      font: { size: 12 },
    },
  };
}

function renderDomainChart(data) {
  const sorted = [...data.domain_horizons].sort((a, b) => b.horizon_p50_minutes - a.horizon_p50_minutes);
  const x = sorted.map((d) => labelDomain(d.domain));
  const y = sorted.map((d) => d.horizon_p50_minutes);
  const low = sorted.map((d) => Math.max(d.horizon_p50_minutes - d.horizon_ci_low_minutes, 0));
  const high = sorted.map((d) => Math.max(d.horizon_ci_high_minutes - d.horizon_p50_minutes, 0));

  const trace = {
    type: "bar",
    x,
    y,
    marker: {
      color: sorted.map((d) => colorDomain(d.domain)),
      line: { color: "#ffffff", width: 1.2 },
    },
    hovertemplate: "<b>%{x}</b><br>Horizon: %{y:.1f} min<extra></extra>",
    error_y: { type: "data", symmetric: false, array: high, arrayminus: low },
  };

  const layout = {
    ...layoutBase(),
    title: { text: "Time Horizon by Domain", x: 0.02, xanchor: "left" },
    xaxis: { ...axisBase(), tickangle: -15 },
    yaxis: { ...axisBase(), title: "Horizon (minutes)" },
  };

  Plotly.newPlot("domain-chart", [trace], layout, CHART_CONFIG);
}

function shortModelName(name) {
  return name.replace(" (Inspect)", "");
}

function renderTokenEfficiency(data) {
  const econ = data.agent_economics || {};
  const models = (econ.models || [])
    .filter((m) => Number.isFinite(m.tokens_per_success_hour))
    .sort((a, b) => a.tokens_per_success_hour - b.tokens_per_success_hour)
    .slice(0, 12);

  const trace = {
    type: "bar",
    x: models.map((m) => shortModelName(m.model)),
    y: models.map((m) => m.tokens_per_success_hour),
    marker: {
      color: models.map((m) => m.tokens_per_success_hour),
      colorscale: "Tealgrn",
      reversescale: true,
      line: { color: "#ffffff", width: 1.1 },
    },
    hovertemplate: "<b>%{x}</b><br>%{y:,.0f} tokens / successful hour<extra></extra>",
  };

  Plotly.newPlot(
    "token-efficiency-chart",
    [trace],
    {
      ...layoutBase(),
      title: { text: "Option A: Token Efficiency (Lower is Better)", x: 0.02, xanchor: "left" },
      xaxis: { ...axisBase(), tickangle: -20 },
      yaxis: { ...axisBase(), title: "Tokens per successful autonomous hour" },
    },
    CHART_CONFIG
  );
}

function renderCostEfficiency(data, presetKey) {
  const econ = data.agent_economics || {};
  const models = (econ.models || [])
    .filter((m) => m.estimated_cost_scenarios && m.estimated_cost_scenarios[presetKey])
    .map((m) => ({
      model: m.model,
      usd: m.estimated_cost_scenarios[presetKey].usd_per_autonomous_hour,
    }))
    .filter((m) => Number.isFinite(m.usd))
    .sort((a, b) => a.usd - b.usd)
    .slice(0, 12);

  const trace = {
    type: "bar",
    x: models.map((m) => shortModelName(m.model)),
    y: models.map((m) => m.usd),
    marker: {
      color: models.map((m) => m.usd),
      colorscale: "Sunset",
      reversescale: true,
      line: { color: "#ffffff", width: 1.1 },
    },
    hovertemplate: "<b>%{x}</b><br>$%{y:.2f} per autonomous hour<extra></extra>",
  };

  Plotly.newPlot(
    "cost-efficiency-chart",
    [trace],
    {
      ...layoutBase(),
      title: { text: "Option B: Estimated Cost per Autonomous Hour", x: 0.02, xanchor: "left" },
      xaxis: { ...axisBase(), tickangle: -20 },
      yaxis: { ...axisBase(), title: "Estimated USD per autonomous hour" },
    },
    CHART_CONFIG
  );
}

function setupSplitSelector(data) {
  const econ = data.agent_economics || {};
  const splitPresets = econ.split_presets || {};
  const select = document.getElementById("split-select");
  const note = document.getElementById("split-note");
  select.innerHTML = "";

  const keys = Object.keys(splitPresets);
  keys.forEach((key) => {
    const preset = splitPresets[key];
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = preset.label || key;
    select.appendChild(opt);
  });

  const defaultKey = keys.includes("input_70_output_30") ? "input_70_output_30" : keys[0];
  if (defaultKey) {
    select.value = defaultKey;
    renderCostEfficiency(data, defaultKey);
  }

  const updateNote = () => {
    const preset = splitPresets[select.value];
    if (!preset) {
      note.textContent = "";
      return;
    }
    note.textContent = `Assumption: ${Math.round(preset.input_share * 100)}% input, ${Math.round(
      preset.output_share * 100
    )}% output. Source data does not contain input/output split.`;
  };

  select.addEventListener("change", () => {
    renderCostEfficiency(data, select.value);
    updateNote();
  });

  updateNote();
}

function renderModelSelector(data) {
  const select = document.getElementById("model-select");
  const models = [...new Set(data.model_domain.map((r) => r.model))].sort();
  models.forEach((model) => {
    const opt = document.createElement("option");
    opt.value = model;
    opt.textContent = model;
    select.appendChild(opt);
  });
  if (models.length) {
    select.value = models[0];
  }
  return select;
}

function renderModelChart(data, model) {
  const rows = data.curves.filter((c) => c.model === model);
  const traces = rows.map((row) => ({
    type: "scatter",
    mode: "lines+markers",
    name: labelDomain(row.domain),
    x: row.points.map((p) => p.minutes),
    y: row.points.map((p) => p.success * 100),
    line: {
      width: 3,
      shape: "spline",
      smoothing: 0.35,
      color: colorDomain(row.domain),
    },
    marker: {
      size: 8,
      color: colorDomain(row.domain),
      line: { color: "#ffffff", width: 1.6 },
    },
    hovertemplate: "<b>%{fullData.name}</b><br>Task length: %{x:.1f} min<br>Success: %{y:.1f}%<extra></extra>",
  }));

  const layout = {
    ...layoutBase(),
    title: { text: `${shortModelName(model)}: Success Curves by Domain`, x: 0.02, xanchor: "left" },
    xaxis: { ...axisBase(), title: "Human task duration (minutes)", type: "log" },
    yaxis: { ...axisBase(), title: "Success probability (%)", range: [0, 100] },
    hovermode: "x unified",
  };

  Plotly.newPlot("model-chart", traces, layout, CHART_CONFIG);
}

function renderForecast(data, doublingMonths) {
  const targets = [60, 8 * 60, 24 * 60];
  const names = ["1h", "8h", "1d"];
  const rows = data.domain_horizons.map((d) => {
    const baseline = Math.max(d.horizon_p50_minutes || 1, 1e-6);
    const baselineDate = new Date(data.generated_at);
    const monthsToTarget = targets.map((target) => {
      if (baseline >= target) return 0;
      return Math.log2(target / baseline) * doublingMonths;
    });
    return { domain: d.domain, baselineDate, monthsToTarget };
  });

  const traces = names.map((name, i) => ({
    type: "bar",
    name,
    x: rows.map((r) => labelDomain(r.domain)),
    y: rows.map((r) => r.monthsToTarget[i]),
    marker: {
      color: ["#4f77b4", "#3f9e8b", "#c85663"][i],
      line: { color: "#ffffff", width: 1.0 },
    },
    hovertemplate: "<b>%{x}</b><br>Months to target: %{y:.1f}<extra></extra>",
  }));

  Plotly.newPlot(
    "forecast-chart",
    traces,
    {
      ...layoutBase(),
      title: { text: "Forecast Explorer", x: 0.02, xanchor: "left" },
      barmode: "group",
      xaxis: { ...axisBase(), tickangle: -15 },
      yaxis: { ...axisBase(), title: "Months to reach target" },
    },
    CHART_CONFIG
  );
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

async function init() {
  try {
    const data = await loadData();
    renderDomainChart(data);

    const select = renderModelSelector(data);
    renderModelChart(data, select.value);
    select.addEventListener("change", () => renderModelChart(data, select.value));

    const slider = document.getElementById("doubling-slider");
    const doublingValue = document.getElementById("doubling-value");
    const render = () => {
      doublingValue.textContent = `${slider.value} months`;
      renderForecast(data, Number(slider.value));
    };
    slider.addEventListener("input", render);
    render();

    renderTokenEfficiency(data);
    setupSplitSelector(data);

    renderTable(data);
    document.getElementById("generated-at").textContent = `Generated at: ${data.generated_at}`;
  } catch (error) {
    console.error(error);
    document.body.innerHTML += `<p style=\"padding:1rem;color:#991b1b\">${error.message}</p>`;
  }
}

window.addEventListener("DOMContentLoaded", init);
