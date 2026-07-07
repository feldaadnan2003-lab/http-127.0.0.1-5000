/* Renders the two dashboard summary charts using data injected by dashboard.html */
document.addEventListener("DOMContentLoaded", () => {
  if (!window.DASHBOARD_DATA) return;

  const categoryCanvas = document.getElementById("categoryChart");
  if (categoryCanvas) {
    new Chart(categoryCanvas, {
      type: "bar",
      data: {
        labels: window.DASHBOARD_DATA.categories.labels,
        datasets: [
          {
            label: "Reports",
            data: window.DASHBOARD_DATA.categories.values,
            backgroundColor: CHART_PALETTE,
            borderRadius: 8,
            maxBarThickness: 42,
          },
        ],
      },
      options: baseChartOptions({ plugins: { legend: { display: false } } }),
    });
  }

  const priorityCanvas = document.getElementById("priorityChart");
  if (priorityCanvas) {
    new Chart(priorityCanvas, {
      type: "doughnut",
      data: {
        labels: window.DASHBOARD_DATA.priorities.labels,
        datasets: [
          {
            data: window.DASHBOARD_DATA.priorities.values,
            backgroundColor: CHART_PALETTE,
            borderWidth: 2,
          },
        ],
      },
      options: pieOptions(),
    });
  }
});
