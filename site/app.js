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

    renderTable(data);
    document.getElementById("generated-at").textContent = `Generated at: ${data.generated_at}`;
  } catch (error) {
    console.error(error);
    document.body.innerHTML += `<p style=\"padding:1rem;color:#991b1b\">${error.message}</p>`;
  }
}

window.addEventListener("DOMContentLoaded", init);
