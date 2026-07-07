/* Shared behavior across all pages: loader, scroll-reveal, sidebar, dropdowns, notifications, search. */
document.addEventListener("DOMContentLoaded", () => {
  hidePageLoader();
  initScrollReveal();
  initMobileNav();
  initSidebarToggle();
  initDropdowns();
  initNotifications();
  initGlobalSearch();
  initFaq();
  initFlashAutoDismiss();
  initAnimatedCounters();
});

function hidePageLoader() {
  const loader = document.getElementById("page-loader");
  if (!loader) return;
  setTimeout(() => loader.classList.add("hidden"), 250);
}

function initScrollReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  items.forEach((item) => observer.observe(item));
}

function initMobileNav() {
  const btn = document.getElementById("mobileMenuBtn");
  const links = document.getElementById("navLinks");
  if (!btn || !links) return;
  btn.addEventListener("click", () => links.classList.toggle("open"));
}

function initSidebarToggle() {
  const btn = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  if (!btn || !sidebar) return;
  btn.addEventListener("click", () => sidebar.classList.toggle("open"));
}

function initDropdowns() {
  const pairs = [
    { trigger: "notificationBtn", panel: "notificationPanel" },
    { trigger: "userMenuBtn", panel: "userMenuPanel" },
  ];

  pairs.forEach(({ trigger, panel }) => {
    const triggerEl = document.getElementById(trigger);
    const panelEl = document.getElementById(panel);
    if (!triggerEl || !panelEl) return;

    triggerEl.addEventListener("click", (event) => {
      event.stopPropagation();
      document.querySelectorAll(".dropdown-panel.show").forEach((p) => {
        if (p !== panelEl) p.classList.remove("show");
      });
      panelEl.classList.toggle("show");
    });
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".dropdown-panel")) {
      document.querySelectorAll(".dropdown-panel.show").forEach((p) => p.classList.remove("show"));
    }
  });
}

function initNotifications() {
  const list = document.getElementById("notificationList");
  const btn = document.getElementById("notificationBtn");
  if (!list || !btn) return;

  let loaded = false;

  btn.addEventListener("click", () => {
    if (loaded) return;
    loaded = true;

    fetch("/api/notifications")
      .then((res) => res.json())
      .then((notifications) => {
        if (!notifications.length) {
          list.innerHTML = '<div class="empty-state-small">No notifications yet.</div>';
          return;
        }
        list.innerHTML = notifications
          .map(
            (n) => `
            <div class="notification-item ${n.is_read ? "" : "unread"}" data-id="${n.id}">
              <div>${escapeHtml(n.message)}</div>
              <div class="notification-time">${n.created_at}</div>
            </div>`
          )
          .join("");
      })
      .catch(() => {
        list.innerHTML = '<div class="empty-state-small">Could not load notifications.</div>';
      });
  });
}

function initGlobalSearch() {
  const input = document.getElementById("globalSearch");
  const resultsBox = document.getElementById("searchResults");
  if (!input || !resultsBox) return;

  let debounceTimer;
  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = input.value.trim();
    if (query.length < 2) {
      resultsBox.classList.remove("show");
      return;
    }
    debounceTimer = setTimeout(() => runSearch(query), 300);
  });

  function runSearch(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((results) => {
        if (!results.length) {
          resultsBox.innerHTML = '<div class="empty-state-small">No matching reports.</div>';
        } else {
          resultsBox.innerHTML = results
            .map(
              (r) => `
              <a class="search-result-item" href="${r.url}">
                <div class="search-result-title">${escapeHtml(r.title)}</div>
                <div class="search-result-meta">${escapeHtml(r.ministry)} &middot; ${escapeHtml(r.category || "")}</div>
              </a>`
            )
            .join("");
        }
        resultsBox.classList.add("show");
      });
  }

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".topbar-search")) resultsBox.classList.remove("show");
  });
}

function initFaq() {
  document.querySelectorAll(".faq-question").forEach((question) => {
    question.addEventListener("click", () => {
      const item = question.closest(".faq-item");
      const wasOpen = item.classList.contains("open");
      document.querySelectorAll(".faq-item.open").forEach((el) => el.classList.remove("open"));
      if (!wasOpen) item.classList.add("open");
    });
  });
}

function initFlashAutoDismiss() {
  document.querySelectorAll(".toast").forEach((toast) => {
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  });
}

function initAnimatedCounters() {
  const counters = document.querySelectorAll(".stat-number[data-count]");
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.4 }
  );
  counters.forEach((counter) => observer.observe(counter));
}

function animateCounter(el) {
  const target = parseFloat(el.dataset.count);
  const decimals = parseInt(el.dataset.decimal || "0", 10);
  const duration = 1400;
  const start = performance.now();

  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = target * eased;
    el.textContent = decimals ? value.toFixed(decimals) : Math.round(value).toLocaleString();
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : str;
  return div.innerHTML;
}
