"""Utility to return the appropriate currency symbol/abbreviation for a ticker.

- Indian NSE/BSE stocks (BSE Sensex & NSE Nifty 50) -> "Rs"
- US stocks (Nasdaq-100) -> "USD"
"""

def get_currency(ticker: str) -> str:
    """Return 'Rs' for Indian stocks, 'USD' for US stocks.
    Simplified logic based on ticker suffix and known index symbols.
    """
    if not ticker:
        return ""
    t = ticker.upper().strip()
    # Index symbols
    if t in {"^NSEI", "^BSESN", "^NSEBANK"}:
        return "Rs"
    if t in {"^IXIC", "^GSPC", "^DJI", "^NDX"}:
        return "USD"
    # Exchange suffixes
    if t.endswith('.NS') or t.endswith('.BO'):
        return "Rs"
    # Fallback: assume US
    return "USD"
