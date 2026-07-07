/* Shared Chart.js theming helpers used by dashboard.js and analytics.js */

const CHART_PALETTE = [
  "#0a5cd4", "#0f9d58", "#1abc9c", "#f59e0b", "#e11d48",
  "#7c3aed", "#0891b2", "#e2662c", "#64748b", "#2563eb",
];

function isDarkMode() {
  return document.documentElement.getAttribute("data-theme") === "dark";
}

function chartTextColor() {
  return isDarkMode() ? "#a9b6cc" : "#4a5b70";
}

function chartGridColor() {
  return isDarkMode() ? "#24304a" : "#e3e9f1";
}

function baseChartOptions(extra = {}) {
  return Object.assign(
    {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: chartTextColor(), font: { family: "Inter", size: 12 } },
        },
        tooltip: { padding: 10, cornerRadius: 8 },
      },
      scales: {
        x: { ticks: { color: chartTextColor() }, grid: { color: chartGridColor() } },
        y: { ticks: { color: chartTextColor() }, grid: { color: chartGridColor() } },
      },
    },
    extra
  );
}

function pieOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "bottom", labels: { color: chartTextColor(), font: { family: "Inter", size: 12 } } },
    },
  };
}
