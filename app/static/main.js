/* =====================================================================
   Intelligent Financial Platform – main.js
   Theme toggle + index page interactivity
   ===================================================================== */

(function () {
  'use strict';

  /* ── Theme ─────────────────────────────────────────────────────────── */
  const root = document.documentElement;
  const STORAGE_KEY = 'ifp-theme';

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function initTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    const preferred = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(preferred);
  }

  function toggleTheme() {
    const current = root.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  initTheme();

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.addEventListener('click', toggleTheme);

    /* ── Advanced settings accordion ─────────────────────────────────── */
    const advToggle = document.getElementById('advanced-toggle');
    const advBody   = document.getElementById('advanced-body');
    if (advToggle && advBody) {
      advToggle.addEventListener('click', function () {
        const open = advBody.classList.toggle('open');
        advToggle.classList.toggle('open', open);
      });
    }

    /* ── Market → Company dropdown ───────────────────────────────────── */
    const marketSel  = document.getElementById('market-select');
    const companySel = document.getElementById('company-select');
    const marketMap  = window.MARKET_MAP || {};

    function populateCompanies() {
      if (!marketSel || !companySel) return;
      const market = marketSel.value;
      const companies = marketMap[market] || [];
      companySel.innerHTML = '';
      companies.forEach(function (c) {
        const opt = document.createElement('option');
        opt.value = c.ticker;
        opt.textContent = c.ticker + ' – ' + c.name;
        companySel.appendChild(opt);
      });
    }

    if (marketSel) {
      marketSel.addEventListener('change', populateCompanies);
      populateCompanies();
    }

    /* ── Form submit → loading state ────────────────────────────────── */
    const form = document.getElementById('forecast-form');
    const submitBtn = document.getElementById('submit-btn');
    if (form && submitBtn) {
      form.addEventListener('submit', function () {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="btn-spinner"></span> Running…';
      });
    }

    /* ── Select all / none model helpers ────────────────────────────── */
    const selectAll  = document.getElementById('select-all-models');
    const selectNone = document.getElementById('select-none-models');
    if (selectAll) {
      selectAll.addEventListener('click', function () {
        document.querySelectorAll('.model-chip input[type="checkbox"]').forEach(cb => cb.checked = true);
      });
    }
    if (selectNone) {
      selectNone.addEventListener('click', function () {
        document.querySelectorAll('.model-chip input[type="checkbox"]').forEach(cb => cb.checked = false);
      });
    }
  });
})();
