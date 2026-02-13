async function loadData() {
  const response = await fetch("./data.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Cannot load data.json (${response.status})`);
  }
  return response.json();
}

function renderDomainChart(data) {
  const x = data.domain_horizons.map((d) => d.domain);
  const y = data.domain_horizons.map((d) => d.horizon_p50_minutes);
  const low = data.domain_horizons.map((d) => Math.max(d.horizon_p50_minutes - d.horizon_ci_low_minutes, 0));
  const high = data.domain_horizons.map((d) => Math.max(d.horizon_ci_high_minutes - d.horizon_p50_minutes, 0));

  const trace = {
    type: "bar",
    x,
    y,
    marker: { color: "#0f766e" },
    error_y: { type: "data", symmetric: false, array: high, arrayminus: low },
  };

  Plotly.newPlot("domain-chart", [trace], {
    margin: { t: 10 },
    yaxis: { title: "Horizon (minutes)" },
  }, { responsive: true });
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
    marker: { color: "#1d4ed8" },
  };

  Plotly.newPlot(
    "token-efficiency-chart",
    [trace],
    {
      margin: { t: 10 },
      xaxis: { tickangle: -25 },
      yaxis: { title: "Tokens per successful autonomous hour" },
    },
    { responsive: true }
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
    marker: { color: "#0f766e" },
  };

  Plotly.newPlot(
    "cost-efficiency-chart",
    [trace],
    {
      margin: { t: 10 },
      xaxis: { tickangle: -25 },
      yaxis: { title: "Estimated USD per autonomous hour" },
    },
    { responsive: true }
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
    name: row.domain,
    x: row.points.map((p) => p.minutes),
    y: row.points.map((p) => p.success),
  }));

  Plotly.newPlot("model-chart", traces, {
    margin: { t: 10 },
    xaxis: { title: "Human minutes", type: "log" },
    yaxis: { title: "Success probability", range: [0, 1] },
  }, { responsive: true });
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
    x: rows.map((r) => r.domain),
    y: rows.map((r) => r.monthsToTarget[i]),
  }));

  Plotly.newPlot("forecast-chart", traces, {
    barmode: "group",
    margin: { t: 10 },
    yaxis: { title: "Months to reach target" },
  }, { responsive: true });
}

function renderTable(data) {
  const tbody = document.querySelector("#records-table tbody");
  tbody.innerHTML = "";
  data.table_rows.slice(0, 150).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.benchmark}</td>
      <td>${row.domain}</td>
      <td>${row.model}</td>
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
