"""Technical analysis: MA chart, Bollinger Bands, trend summary."""

import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def plot_moving_average(df, ticker: str = config.TICKER, ax=None):
    """Plot Close price and moving average on provided Axes.
    If *ax* is None a new Figure/Axes is created. Returns the Figure.
    """
    created = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(13, 5))
        created = True
    else:
        fig = ax.figure
    ax.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=1.5)
    ax.plot(df.index, df["MA20"],  label=f"MA{config.MA_WINDOW}", color="#ff7f0e", linestyle="--", linewidth=1.5)
    ax.set_title(f"{ticker} — Close Price & {config.MA_WINDOW}-Day MA", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Price"); ax.legend(); ax.grid(alpha=0.3)
    plt.xticks(rotation=45); plt.tight_layout()
    if created:
        return fig
    return None
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=1.5)
    ax.plot(df.index, df["MA20"],  label=f"MA{config.MA_WINDOW}", color="#ff7f0e", linestyle="--", linewidth=1.5)
    ax.set_title(f"{ticker} — Close Price & {config.MA_WINDOW}-Day MA", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Price"); ax.legend(); ax.grid(alpha=0.3)
    plt.xticks(rotation=45); plt.tight_layout(); plt.show()


def plot_bollinger_bands(df, ticker: str = config.TICKER, ax=None):
    """Plot Bollinger Bands on provided Axes.
    If *ax* is None a new Figure/Axes is created. Returns the Figure.
    """
    upper = df["MA20"] + 2 * df["Volatility"]
    lower = df["MA20"] - 2 * df["Volatility"]
    created = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(13, 5))
        created = True
    else:
        fig = ax.figure
    ax.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=1.5)
    ax.plot(df.index, df["MA20"],  label="MA20",        color="#ff7f0e", linestyle="--", linewidth=1)
    ax.plot(df.index, upper, label="Upper Band (+2s)", color="#2ca02c", linestyle=":", linewidth=1)
    ax.plot(df.index, lower, label="Lower Band (-2s)", color="#d62728", linestyle=":", linewidth=1)
    ax.fill_between(df.index, lower, upper, alpha=0.07, color="grey")
    ax.set_title(f"{ticker} — Bollinger Bands", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Price"); ax.legend(); ax.grid(alpha=0.3)
    plt.xticks(rotation=45); plt.tight_layout()
    if created:
        return fig
    return None
    upper = df["MA20"] + 2 * df["Volatility"]
    lower = df["MA20"] - 2 * df["Volatility"]
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="#1f77b4", linewidth=1.5)
    ax.plot(df.index, df["MA20"],  label="MA20",        color="#ff7f0e", linestyle="--", linewidth=1)
    ax.plot(df.index, upper, label="Upper Band (+2s)", color="#2ca02c", linestyle=":", linewidth=1)
    ax.plot(df.index, lower, label="Lower Band (-2s)", color="#d62728", linestyle=":", linewidth=1)
    ax.fill_between(df.index, lower, upper, alpha=0.07, color="grey")
    ax.set_title(f"{ticker} — Bollinger Bands", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date"); ax.set_ylabel("Price"); ax.legend(); ax.grid(alpha=0.3)
    plt.xticks(rotation=45); plt.tight_layout(); plt.show()


def print_trend_summary(df, ticker: str = config.TICKER):
    """Print plain-English trend signal vs MA20."""
    close   = float(df["Close"].iloc[-1])
    ma      = float(df["MA20"].iloc[-1])
    pct     = (close - ma) / ma * 100
    signal  = ("BULLISH -- price is above its average." if close > ma
               else "BEARISH -- price is below its average." if close < ma
               else "NEUTRAL -- price equals its average.")
    print(f"\n{'─'*50}")
    print(f"  {ticker} | Close: {close:,.2f} | MA{config.MA_WINDOW}: {ma:,.2f} | {pct:+.2f}%")
    print(f"  {signal}")
    print(f"{'─'*50}\n")
