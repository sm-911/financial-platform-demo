"""Stock data: download from Yahoo Finance and engineer ML features."""

import pandas as pd
import yfinance as yf
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

FEATURE_COLS = ["MA20", "Volatility", "Lag_1", "Lag_2", "Lag_3", "Lag_4", "Lag_5", "DayOfWeek", "Month", "Sentiment"]
TARGET_COL   = "Close"


def fetch_raw_data(ticker: str = config.TICKER, period: str = config.PERIOD) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance with exponential back‑off.
    If the network request fails (e.g. sandbox without internet), fall back to a
    bundled CSV file under ``data/sample``. This allows the app to run in
    isolated environments and still produce forecasts for demo purposes.
    """
    import time
    max_retries = 3
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  -> Downloading {ticker} ({period})... (attempt {attempt})")
            df = yf.download(ticker, period=period, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty:
                raise ValueError(f"No data for '{ticker}'. Check the symbol and internet.")
            df.dropna(inplace=True)
            print(f"     {len(df)} days loaded ({df.index[0].date()} to {df.index[-1].date()})")
            return df
        except Exception as e:
            if attempt == max_retries:
                # final attempt – try local fallback before giving up
                fallback_path = Path(__file__).resolve().parent / 'sample' / f"{ticker.upper()}.csv"
            if not fallback_path.exists():
                # Use generic sample if specific ticker not available
                fallback_path = Path(__file__).resolve().parent / 'sample' / "AAPL.csv"
            print(f"    Falling back to local sample data: {fallback_path.name}")
            df = pd.read_csv(fallback_path, parse_dates=['Date'])
            df.set_index('Date', inplace=True)
            return df
            print(f"    Warning: {e}. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff *= 2



def engineer_features(df: pd.DataFrame, sentiment_score: float = 0.0) -> pd.DataFrame:
    """Add MA, volatility, lag prices, calendar, and sentiment columns."""
    df = df.copy()
    df["MA20"]       = df["Close"].rolling(window=config.MA_WINDOW).mean()
    df["Volatility"] = df["Close"].rolling(window=config.MA_WINDOW).std()
    for lag in range(1, 6):
        df[f"Lag_{lag}"] = df["Close"].shift(lag)
    df["DayOfWeek"] = df.index.dayofweek
    df["Month"]     = df.index.month
    df["Sentiment"] = sentiment_score
    df.dropna(inplace=True)
    return df


def train_test_split_df(df: pd.DataFrame, test_ratio: float = config.TEST_SPLIT):
    """Chronological train/test split — never shuffle time-series data."""
    split = int(len(df) * (1 - test_ratio))
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values
    print(f"     Train: {split} rows | Test: {len(df) - split} rows")
    return X[:split], X[split:], y[:split], y[split:], df.index[split:]
