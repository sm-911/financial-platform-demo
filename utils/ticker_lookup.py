"""Ticker lookup utility – now proxies to config.STOCK_OPTIONS."""

from config import STOCK_OPTIONS

# Lazy reverse map from ticker to company name
_TICKER_NAME_MAP = None

def get_company_name(ticker: str) -> str:
    """Return a human‑readable company name for *ticker* using config.STOCK_OPTIONS.
    Falls back to the raw ticker if not found.
    """
    global _TICKER_NAME_MAP
    if _TICKER_NAME_MAP is None:
        _TICKER_NAME_MAP = {v[0]: v[1] for v in STOCK_OPTIONS.values()}
    key = ticker.upper().strip()
    return _TICKER_NAME_MAP.get(key, key)
