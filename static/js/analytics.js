/* Fetches analytics API data and renders pie/bar/line charts plus a heat map table. */
document.addEventListener("DOMContentLoaded", () => {
  loadCategoryPie();
  loadRiskPie();
  loadMonthlyLine();
  loadMinistryBar();
  loadHeatmap();
});

function loadCategoryPie() {
  fetch("/analytics/api/category-distribution")
    .then((res) => res.json())
    .then((data) => {
      const canvas = document.getElementById("pieCategoryChart");
      if (!canvas) return;
      new Chart(canvas, {
        type: "pie",
        data: {
          labels: data.labels,
          datasets: [{ data: data.values, backgroundColor: CHART_PALETTE, borderWidth: 2 }],
        },
        options: pieOptions(),
      });
    });
}

function loadRiskPie() {
  fetch("/analytics/api/risk-levels")
    .then((res) => res.json())
    .then((data) => {
      const canvas = document.getElementById("riskPieChart");
      if (!canvas) return;
      const riskColors = { Low: "#0f9d58", Medium: "#f59e0b", High: "#e2662c", Critical: "#e11d48" };
      new Chart(canvas, {
        type: "doughnut",
        data: {
          labels: data.labels,
          datasets: [
            {
              data: data.values,
              backgroundColor: data.labels.map((l) => riskColors[l] || "#64748b"),
              borderWidth: 2,
            },
          ],
        },
        options: pieOptions(),
      });
    });
}

function loadMonthlyLine() {
  fetch("/analytics/api/monthly-reports")
    .then((res) => res.json())
    .then((data) => {
      const canvas = document.getElementById("monthlyLineChart");
      if (!canvas) return;
      new Chart(canvas, {
        type: "line",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Reports Submitted",
              data: data.values,
              borderColor: "#0a5cd4",
              backgroundColor: "rgba(10, 92, 212, 0.12)",
              fill: true,
              tension: 0.35,
              pointRadius: 4,
              pointBackgroundColor: "#0a5cd4",
            },
          ],
        },
        options: baseChartOptions(),
      });
    });
}

function loadMinistryBar() {
  fetch("/analytics/api/ministry-comparison")
    .then((res) => res.json())
    .then((data) => {
      const canvas = document.getElementById("ministryBarChart");
      if (!canvas) return;
      new Chart(canvas, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Performance Score (%)",
              data: data.performance,
              backgroundColor: "#0a5cd4",
              borderRadius: 6,
            },
            {
              label: "Avg. Resolution Days",
              data: data.resolution_days,
              backgroundColor: "#1abc9c",
              borderRadius: 6,
            },
          ],
        },
        options: baseChartOptions(),
      });
    });
}

function loadHeatmap() {
  fetch("/analytics/api/heatmap")
    .then((res) => res.json())
    .then((data) => {
      const container = document.getElementById("heatmapContainer");
      if (!container) return;

      const max = Math.max(1, ...data.matrix.flat());

      let html = '<table class="heatmap-table"><thead><tr><th>Ministry</th>';
      data.months.forEach((m) => (html += `<th>${m}</th>`));
      html += "</tr></thead><tbody>";

      data.ministries.forEach((ministry, rowIndex) => {
        html += `<tr><td>${ministry}</td>`;
        data.matrix[rowIndex].forEach((value) => {
          const intensity = value / max;
          const bg = `rgba(10, 92, 212, ${0.08 + intensity * 0.75})`;
          html += `<td class="heatmap-cell" style="background:${bg}">${value}</td>`;
        });
        html += "</tr>";
      });
      html += "</tbody></table>";
      container.innerHTML = html;
    });
}
