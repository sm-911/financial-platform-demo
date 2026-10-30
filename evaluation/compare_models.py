"""Model evaluation: RMSE/MAE/R², comparison table, and clear actual vs predicted chart."""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.currency import get_currency


def _resolve_ticker(ticker: str = None) -> str:
    """Helper to resolve the active ticker from argument, notebook __main__, or config."""
    if ticker:
        return ticker
    try:
        import __main__
        if hasattr(__main__, "TICKER") and __main__.TICKER:
            return str(__main__.TICKER)
    except Exception:
        pass
    return getattr(config, "TICKER", "TSLA")


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute evaluation metrics.
    Returns a dict with **lower‑case** keys matching the template:
    - ``rmse``   : Root Mean Squared Error
    - ``mae``    : Mean Absolute Error
    - ``mape``   : Mean Absolute Percentage Error (percentage)
    - ``r2``     : Coefficient of Determination
    """
    n = min(len(y_true), len(y_pred))
    yt = np.asarray(y_true)[-n:]
    yp = np.asarray(y_pred)[-n:]
    # RMSE
    rmse = float(np.sqrt(mean_squared_error(yt, yp)))
    # MAE
    mae = float(mean_absolute_error(yt, yp))
    # MAPE – avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        perc_err = np.abs((yt - yp) / yt)
        perc_err = perc_err[~np.isnan(perc_err)]
        mape = float(np.mean(perc_err) * 100) if perc_err.size > 0 else float('nan')
    # R2
    r2 = float(r2_score(yt, yp))
    return {"rmse": rmse, "mae": mae, "mape": mape, "r2": r2}


def print_comparison_table(rf: dict, lstm: dict, ticker: str = None) -> None:
    """Print model performance table with dynamic currency units (Rs for Nifty/Sensex, USD for Nasdaq)."""
    resolved_ticker = _resolve_ticker(ticker)
    curr = get_currency(resolved_ticker)
    unit_label = f" {curr}" if curr else ""

    print(f"\n{'='*52}\n   Model Performance Comparison\n{'='*52}")
    print(f"  {'Metric':<10}  {'Random Forest':>15}  {'LSTM':>15}")
    print(f"{'-'*52}")
    for key in ["rmse", "mae", "r2"]:
        # Determine better model: lower is better for rmse/mae, higher for r2
        if key == "r2":
            better = "RF *" if rf[key] >= lstm[key] else "LSTM *"
        else:
            better = "RF *" if rf[key] <= lstm[key] else "LSTM *"
        fmt = ".4f" if key == "r2" else ".2f"
        # Append unit label only for price-based metrics
        if key != "r2":
            rf_str = f"{rf[key]:{fmt}}{unit_label}"
            lstm_str = f"{lstm[key]:{fmt}}{unit_label}"
        else:
            rf_str = f"{rf[key]:{fmt}}"
            lstm_str = f"{lstm[key]:{fmt}}"
        print(f"  {key.upper():<10}  {rf_str:>15}  {lstm_str:>15}   {better}")
    print(f"{'='*52}")
    curr_paren = f"({curr})" if curr else ""
    print(f"  RMSE & MAE -> lower is better {curr_paren} | R2 -> higher is better (max 1.0)")
    print(f"{'='*52}\n")


def print_final_verdict(ticker: str,
                         latest_price: float,
                         ma20: float,
                         sentiment_score: float,
                         rf_metrics: dict,
                         lstm_metrics: dict,
                         next_pred_rf: float,
                         next_pred_lstm: float):
    """Print research breakdown and final deduction with dynamic currency (Rs / USD)."""
    curr = get_currency(ticker)
    curr_prefix = f"{curr} " if curr else ""

    # Technicals
    diff_ma = latest_price - ma20
    pct_ma = (diff_ma / ma20) * 100
    if latest_price > ma20:
        tech_status = f"ABOVE 20-Day MA (Bullish) | Current: {curr_prefix}{latest_price:,.2f} vs MA20: {curr_prefix}{ma20:,.2f} (+{pct_ma:.2f}%)"
    else:
        tech_status = f"BELOW 20-Day MA (Bearish) | Current: {curr_prefix}{latest_price:,.2f} vs MA20: {curr_prefix}{ma20:,.2f} ({pct_ma:.2f}%)"

    # Sentiment
    if sentiment_score > 0.05:
        sent_status = f"POSITIVE (Compound Score: {sentiment_score:+.3f})"
    elif sentiment_score < -0.05:
        sent_status = f"NEGATIVE (Compound Score: {sentiment_score:+.3f})"
    else:
        sent_status = f"NEUTRAL (Compound Score: {sentiment_score:+.3f})"

    # Machine Learning
    best_model = "Random Forest" if rf_metrics["r2"] >= lstm_metrics["r2"] else "LSTM"
    best_r2 = max(rf_metrics["r2"], lstm_metrics["r2"])
    pred_price = next_pred_rf if best_model == "Random Forest" else next_pred_lstm
    diff_pct = ((pred_price - latest_price) / latest_price) * 100
    move_dir = "UPWARD" if diff_pct > 0 else "DOWNWARD"

    ml_status = (
        f"Superior Model: {best_model} (R2 = {best_r2:.4f})\\n"
        f"    * RF R2: {rf_metrics['r2']:.4f} | RMSE: {curr_prefix}{rf_metrics['rmse']:.2f}\\n"
        f"    * LSTM R2: {lstm_metrics['r2']:.4f} | RMSE: {curr_prefix}{lstm_metrics['rmse']:.2f}\\n"
        f"    * Projected Move: {move_dir} ({diff_pct:+.2f}% expected)"
    )


    # Plain-English Conclusion / Deduction
    if latest_price > ma20 and sentiment_score > 0.05:
        conclusion = (
            f"The analysis presents a strong Bullish outlook for {ticker}. Both news sentiment "
            f"and technical trend are positive (price above 20-day MA). {best_model} delivered "
            f"the higher predictive accuracy (R2 = {best_r2:.4f}) and forecasts continued {move_dir} momentum."
        )
    elif latest_price < ma20 and sentiment_score < -0.05:
        conclusion = (
            f"The analysis indicates a Bearish outlook for {ticker}. The stock is trading below "
            f"its 20-day MA accompanied by negative news headlines. {best_model} is the superior model "
            f"(R2 = {best_r2:.4f}) predicting further {move_dir} pressure. Caution is advised."
        )
    else:
        conclusion = (
            f"The analysis indicates Mixed/Neutral market dynamics for {ticker}. While technicals show "
            f"the stock is {'above' if latest_price > ma20 else 'below'} its 20-day MA, news sentiment is "
            f"{sent_status.split()[0].lower()}. The higher-performing model ({best_model}, R2 = {best_r2:.4f}) "
            f"projects a {move_dir} trajectory. Wait for trend-sentiment alignment before making decisions."
        )

    print("\n" + "="*70)
    print("                     RESEARCH SUMMARY & FINAL DEDUCTION")
    print("="*70)
    print("\n[TECHNICALS]")
    print(f"  * {tech_status}")
    print("\n[NEWS SENTIMENT]")
    print(f"  * {sent_status}")
    print("\n[MACHINE LEARNING]")
    print(f"  * {ml_status}")
    print("\n" + "-"*70)
    print("FINAL CONCLUSION & DEDUCTION:")
    print(f"  \"{conclusion}\"")
    print("="*70 + "\n")


def plot_comparison(test_dates, y_true, y_pred_rf, y_pred_lstm, ticker: str = None):
    """Clear, distinct actual vs predicted comparison chart.
    Returns the Matplotlib Figure – the caller will encode it.
    """
    resolved_ticker = _resolve_ticker(ticker)
    curr = get_currency(resolved_ticker)
    n = min(len(y_true), len(y_pred_rf), len(y_pred_lstm))
    dates = test_dates[-n:]

    fig, ax = plt.subplots(figsize=(14, 7), constrained_layout=True)
    ax.plot(dates, y_true[-n:], label="Actual Market Price", color="#111111", linewidth=2.2, zorder=3)
    ax.plot(dates, y_pred_rf[-n:], label="Random Forest", color="#1f77b4", linestyle="--", linewidth=1.8, alpha=0.9, zorder=2)
    ax.plot(dates, y_pred_lstm[-n:], label="LSTM (Neural Net)", color="#2ca02c", linestyle=":", linewidth=2.0, alpha=0.9, zorder=2)
    ax.set_title(f"{resolved_ticker} - Actual vs Predicted Stock Price (Test Period)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ylabel = f"Price ({curr})" if curr else "Price"
    ax.set_ylabel(ylabel, fontsize=11)
    ax.legend(fontsize=11, loc="best", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)
    return fig  # caller will encode to base64


def plot_metrics_bar(rf: dict, lstm: dict):
    """Side-by-side bar chart comparing RF vs LSTM on RMSE, MAE and R²."""
    metrics = ["RMSE", "MAE", "R2"]
    rf_vals   = [rf[m]   for m in metrics]
    lstm_vals = [lstm[m] for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_rf   = ax.bar(x - width / 2, rf_vals,   width, label="Random Forest", color="#1f77b4", alpha=0.9)
    bars_lstm = ax.bar(x + width / 2, lstm_vals, width, label="LSTM",          color="#2ca02c", alpha=0.9)

    for bar in bars_rf + bars_lstm:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.01 * max(rf_vals + lstm_vals),
                f"{h:.3f}", ha="center", va="bottom", fontsize=8)

    ax.set_title("RF vs LSTM — Metric Comparison", fontsize=13, fontweight="bold")
    ax.set_ylabel("Metric Value  (RMSE & MAE in price units; R² is 0–1)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()
