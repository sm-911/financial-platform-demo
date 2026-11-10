/* =====================================================================
   Intelligent Financial Platform – main.js
   Theme toggle + index page interactivity (search bars + autocomplete)
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

  /* ── Autocomplete helper ─────────────────────────────────────────── */
  /**
   * Attaches a live-search autocomplete to an <input> element.
   * @param {object} opts
   *   inputEl    – the text <input>
   *   dropdownEl – the <ul> dropdown
   *   hiddenEl   – hidden <input> that holds the actual submitted value
   *   items      – array of {label, value, badge?}
   *   onSelect   – callback(item) after a selection is made
   */
  function makeAutocomplete(opts) {
    const { inputEl, dropdownEl, hiddenEl, getItems, onSelect } = opts;
    let activeIdx = -1;
    let currentItems = [];

    function open() { dropdownEl.classList.add('open'); }
    function close() { dropdownEl.classList.remove('open'); activeIdx = -1; }

    function render(items) {
      currentItems = items;
      activeIdx = -1;
      dropdownEl.innerHTML = '';
      if (!items.length) { close(); return; }
      items.forEach(function (item, i) {
        const li = document.createElement('li');
        li.setAttribute('role', 'option');
        const badge = item.badge ? `<span class="ticker-badge">${item.badge}</span>` : '';
        li.innerHTML = badge + escHtml(item.label);
        li.addEventListener('mousedown', function (e) {
          e.preventDefault(); // prevent blur before click
          select(item);
        });
        dropdownEl.appendChild(li);
      });
      open();
    }

    function select(item) {
      inputEl.value  = item.label;
      hiddenEl.value = item.value;
      close();
      if (onSelect) onSelect(item);
    }

    function highlight(idx) {
      const lis = dropdownEl.querySelectorAll('li');
      lis.forEach(function (li, i) {
        li.classList.toggle('active', i === idx);
      });
    }

    inputEl.addEventListener('input', function () {
      const q = inputEl.value.trim().toLowerCase();
      hiddenEl.value = ''; // clear selection when user types
      if (!q) { close(); return; }
      const matched = getItems().filter(function (item) {
        return item.label.toLowerCase().includes(q) ||
               (item.badge && item.badge.toLowerCase().includes(q));
      }).slice(0, 60); // cap at 60 results
      render(matched);
    });

    inputEl.addEventListener('keydown', function (e) {
      const lis = dropdownEl.querySelectorAll('li');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, lis.length - 1);
        highlight(activeIdx);
        if (lis[activeIdx]) lis[activeIdx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        highlight(activeIdx);
        if (lis[activeIdx]) lis[activeIdx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        if (activeIdx >= 0 && currentItems[activeIdx]) {
          e.preventDefault();
          select(currentItems[activeIdx]);
        }
      } else if (e.key === 'Escape') {
        close();
      }
    });

    inputEl.addEventListener('focus', function () {
      if (inputEl.value.trim()) inputEl.dispatchEvent(new Event('input'));
    });

    document.addEventListener('click', function (e) {
      if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) close();
    });
  }

  function escHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  /* ── DOMContentLoaded ───────────────────────────────────────────────── */
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

    /* ── Market autocomplete ─────────────────────────────────────────── */
    const marketSearch   = document.getElementById('market-search');
    const marketDropdown = document.getElementById('market-dropdown');
    const marketValue    = document.getElementById('market-value');
    const companyField   = document.getElementById('company-field');
    const companySearch  = document.getElementById('company-search');
    const companyDropdown= document.getElementById('company-dropdown');
    const companyValue   = document.getElementById('company-value');

    const marketMap  = window.MARKET_MAP  || {};
    const marketsArr = window.MARKETS     || [];

    // Build market items list from MARKETS array
    function getMarketItems() {
      return marketsArr.map(function (m) {
        return { label: m.label, value: m.key, badge: m.key };
      });
    }

    if (marketSearch && marketDropdown && marketValue) {
      makeAutocomplete({
        inputEl:    marketSearch,
        dropdownEl: marketDropdown,
        hiddenEl:   marketValue,
        getItems:   getMarketItems,
        onSelect:   function (item) {
          // Show company field and populate with this market's stocks
          if (companyField) companyField.style.display = '';
          if (companySearch) { companySearch.value = ''; }
          if (companyValue)  { companyValue.value  = ''; }
        },
      });
    }

    /* ── Company autocomplete ────────────────────────────────────────── */
    function getCompanyItems() {
      const market = marketValue ? marketValue.value : '';
      const list   = marketMap[market] || [];
      return list.map(function (c) {
        return { label: c.name, value: c.ticker, badge: c.id || c.ticker.split('.')[0] };
      });
    }

    if (companySearch && companyDropdown && companyValue) {
      makeAutocomplete({
        inputEl:    companySearch,
        dropdownEl: companyDropdown,
        hiddenEl:   companyValue,
        getItems:   getCompanyItems,
        onSelect:   null,
      });
    }

    /* ── Form submit → loading state ────────────────────────────────── */
    const form      = document.getElementById('forecast-form');
    const submitBtn = document.getElementById('submit-btn');
    if (form && submitBtn) {
      form.addEventListener('submit', function (e) {
        // Validate hidden fields are filled
        if (!marketValue.value) {
          e.preventDefault();
          marketSearch.focus();
          marketSearch.style.outline = '2px solid red';
          return;
        }
        if (!companyValue.value) {
          e.preventDefault();
          companySearch.focus();
          companySearch.style.outline = '2px solid red';
          return;
        }
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="btn-spinner"></span> Running…';
      });
    }

    /* ── Select all / none model helpers ────────────────────────────── */
    const selectAll  = document.getElementById('select-all-models');
    const selectNone = document.getElementById('select-none-models');
    if (selectAll) {
      selectAll.addEventListener('click', function () {
        const checkboxes = Array.from(document.querySelectorAll('.model-chip input[type="checkbox"]'));
        // Uncheck all first
        checkboxes.forEach(cb => cb.checked = false);
        // Pick up to 3 random models
        const count = Math.min(3, checkboxes.length);
        for (let i = 0; i < count; i++) {
          const idx = Math.floor(Math.random() * checkboxes.length);
          const cb = checkboxes.splice(idx, 1)[0]; // remove chosen
          if (cb) cb.checked = true;
        }
      });
    }
    if (selectNone) {
      selectNone.addEventListener('click', function () {
        document.querySelectorAll('.model-chip input[type="checkbox"]').forEach(cb => cb.checked = false);
      });
    }
  });
})();
