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

    /* ── Multi-Tier Exchange -> Index -> Stock Flow ────────────────── */
    const exchangeSelect  = document.getElementById('exchange-select');
    const indexField      = document.getElementById('index-field');
    const indexSearch     = document.getElementById('index-search');
    const indexDropdown   = document.getElementById('index-dropdown');
    const indexValue      = document.getElementById('index-value');
    const companyField    = document.getElementById('company-field');
    const companySearch   = document.getElementById('company-search');
    const companyDropdown = document.getElementById('company-dropdown');
    const companyValue    = document.getElementById('company-value');
    const companyBadge    = document.getElementById('company-selected-badge');

    const exchangesArr = window.EXCHANGES || [];
    const indicesMap   = window.INDICES   || {};
    const indexStocks  = window.INDEX_STOCKS || {};

    let currentExchange = '';
    let currentIndex = 'ALL';
    let currentStockList = [];

    // Helper: populate and configure index selector for selected exchange
    function handleExchangeChange(exKey) {
      currentExchange = exKey;
      if (!currentExchange) {
        if (indexField) indexField.style.display = 'none';
        if (companyField) companyField.style.display = 'none';
        return;
      }

      // Show index field
      if (indexField) indexField.style.display = '';
      if (companyField) companyField.style.display = '';

      const indicesForEx = indicesMap[currentExchange] || [];
      // Non-"ALL" indices
      const specificIndices = indicesForEx.filter(i => i.key !== 'ALL');

      // Rule: if only 1 index exists for this exchange, auto-select it!
      if (specificIndices.length === 1) {
        currentIndex = specificIndices[0].key;
        if (indexSearch) indexSearch.value = specificIndices[0].label;
        if (indexValue) indexValue.value = currentIndex;
      } else {
        // Default to ALL (search whole exchange) while allowing user to pick an index
        currentIndex = 'ALL';
        if (indexSearch) indexSearch.value = 'All ' + currentExchange + ' Stocks (No Index Filter)';
        if (indexValue) indexValue.value = 'ALL';
      }

      // Reset stock input
      if (companySearch) { companySearch.value = ''; companySearch.placeholder = 'Search ' + currentExchange + ' stocks…'; }
      if (companyValue) companyValue.value = '';
      if (companyBadge) companyBadge.style.display = 'none';

      // Load stock pool for immediate autocomplete
      loadStocksForCurrentSelection();
    }

    if (exchangeSelect) {
      exchangeSelect.addEventListener('change', function () {
        handleExchangeChange(exchangeSelect.value);
      });
    }

    /* ── Index Autocomplete ─────────────────────────────────────────── */
    function getIndexItems() {
      if (!currentExchange) return [];
      const list = indicesMap[currentExchange] || [];
      return list.map(function (idx) {
        return {
          label: idx.label,
          value: idx.key,
          badge: idx.key === 'ALL' ? 'ALL' : 'INDEX'
        };
      });
    }

    if (indexSearch && indexDropdown && indexValue) {
      makeAutocomplete({
        inputEl:    indexSearch,
        dropdownEl: indexDropdown,
        hiddenEl:   indexValue,
        getItems:   getIndexItems,
        onSelect:   function (item) {
          currentIndex = item.value;
          // Reset stock selection
          if (companySearch) companySearch.value = '';
          if (companyValue) companyValue.value = '';
          if (companyBadge) companyBadge.style.display = 'none';
          loadStocksForCurrentSelection();
        }
      });
    }

    /* ── Stock Autocomplete with server-side / local fallback ────────── */
    function loadStocksForCurrentSelection() {
      // If a specific index is selected and cached locally in window.INDEX_STOCKS
      if (currentIndex && currentIndex !== 'ALL' && indexStocks[currentIndex]) {
        currentStockList = indexStocks[currentIndex];
      } else {
        // Fetch top initial results from backend
        fetch(`/api/stocks?exchange=${encodeURIComponent(currentExchange)}&index=${encodeURIComponent(currentIndex)}&limit=100`)
          .then(res => res.json())
          .then(data => {
            currentStockList = data;
          })
          .catch(err => {
            console.error('Error fetching initial stocks:', err);
          });
      }
    }

    // Dynamic stock autocomplete logic with debounced live search for large universes
    let stockSearchTimer = null;
    if (companySearch && companyDropdown && companyValue) {
      let activeIdx = -1;
      let currentItems = [];

      function open() { companyDropdown.classList.add('open'); }
      function close() { companyDropdown.classList.remove('open'); activeIdx = -1; }

      function render(items) {
        currentItems = items;
        activeIdx = -1;
        companyDropdown.innerHTML = '';
        if (!items.length) {
          const emptyLi = document.createElement('li');
          emptyLi.style.color = 'var(--text-muted, #718096)';
          emptyLi.style.cursor = 'default';
          emptyLi.textContent = 'No matching stocks found';
          companyDropdown.appendChild(emptyLi);
          open();
          return;
        }
        items.forEach(function (item) {
          const li = document.createElement('li');
          li.setAttribute('role', 'option');
          const badge = item.id ? `<span class="ticker-badge">${item.id}</span>` : '';
          li.innerHTML = badge + escHtml(item.name || item.ticker);
          li.addEventListener('mousedown', function (e) {
            e.preventDefault();
            select(item);
          });
          companyDropdown.appendChild(li);
        });
        open();
      }

      function select(item) {
        companySearch.value = item.name + ' (' + (item.id || item.ticker) + ')';
        companyValue.value  = item.ticker;
        if (companyBadge) {
          companyBadge.textContent = 'Selected: ' + item.ticker;
          companyBadge.style.display = 'block';
        }
        close();
      }

      function highlight(idx) {
        const lis = companyDropdown.querySelectorAll('li');
        lis.forEach(function (li, i) {
          li.classList.toggle('active', i === idx);
        });
      }

      function queryStocks(query) {
        const q = query.toLowerCase();
        // If we have index constituents in memory, filter client-side for lightning-fast UX
        if (currentIndex && currentIndex !== 'ALL' && indexStocks[currentIndex]) {
          const matched = indexStocks[currentIndex].filter(function (s) {
            return (s.name && s.name.toLowerCase().includes(q)) ||
                   (s.id && s.id.toLowerCase().includes(q)) ||
                   (s.ticker && s.ticker.toLowerCase().includes(q));
          }).slice(0, 60);
          render(matched);
        } else {
          // Query the API endpoint across the entire exchange
          fetch(`/api/stocks?exchange=${encodeURIComponent(currentExchange)}&index=${encodeURIComponent(currentIndex)}&q=${encodeURIComponent(q)}&limit=60`)
            .then(res => res.json())
            .then(data => {
              render(data);
            })
            .catch(err => {
              console.error('Search error:', err);
            });
        }
      }

      companySearch.addEventListener('input', function () {
        const q = companySearch.value.trim();
        companyValue.value = '';
        if (companyBadge) companyBadge.style.display = 'none';

        if (!q) {
          // Show default initial list
          if (currentStockList.length) render(currentStockList.slice(0, 40));
          else close();
          return;
        }

        clearTimeout(stockSearchTimer);
        stockSearchTimer = setTimeout(function () {
          queryStocks(q);
        }, 150); // 150ms debounce
      });

      companySearch.addEventListener('focus', function () {
        if (!companySearch.value.trim() && currentStockList.length) {
          render(currentStockList.slice(0, 40));
        } else if (companySearch.value.trim()) {
          queryStocks(companySearch.value.trim());
        }
      });

      companySearch.addEventListener('keydown', function (e) {
        const lis = companyDropdown.querySelectorAll('li[role="option"]');
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

      document.addEventListener('click', function (e) {
        if (!companySearch.contains(e.target) && !companyDropdown.contains(e.target)) close();
      });
    }

    /* ── Form submit → loading state ────────────────────────────────── */
    const form      = document.getElementById('forecast-form');
    const submitBtn = document.getElementById('submit-btn');
    if (form && submitBtn) {
      form.addEventListener('submit', function (e) {
        // Validate exchange
        if (exchangeSelect && !exchangeSelect.value) {
          e.preventDefault();
          exchangeSelect.focus();
          exchangeSelect.style.outline = '2px solid red';
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
