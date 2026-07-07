/* Light / Dark mode toggle, persisted in localStorage. */
(function () {
  const STORAGE_KEY = "gov-dss-theme";
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    document.querySelectorAll(".theme-toggle-btn i").forEach((icon) => {
      icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    });
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (prefersDark ? "dark" : "light"));

  document.addEventListener("click", (event) => {
    const btn = event.target.closest(".theme-toggle-btn");
    if (!btn) return;
    const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem(STORAGE_KEY, next);
  });
})();
