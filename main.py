"""Intelligent Financial Research & Analysis Platform — entry point.
Supports 150 pre-configured stocks across BSE Sensex, NSE Nifty 50, and Nasdaq-100.
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore")

import nltk
nltk.download("vader_lexicon", quiet=True)

import config
from data.stock_data import fetch_raw_data, engineer_features, train_test_split_df
from analysis.technical import plot_moving_average, plot_bollinger_bands, print_trend_summary
from analysis.sentiment import fetch_headlines, analyze_sentiment, print_sentiment_report, plot_sentiment_distribution
from models.random_forest import train_random_forest, plot_feature_importance
from models.lstm_model import prepare_lstm_data, train_lstm, predict_lstm, plot_training_loss
from evaluation.compare_models import compute_metrics, print_comparison_table, plot_comparison, plot_metrics_bar


def _display_stock_grid(keys: list[str], title: str):
    """Print stocks neatly in aligned columns."""
    print(f"\n--- {title} ({len(keys)} stocks) ---")
    for k in keys:
        ticker, company, cat = config.STOCK_OPTIONS[k]
        print(f"  [{k:>3}] {ticker:<15} - {company:<32} [{cat}]")
    print("-" * 65)


def select_stock() -> tuple[str, str]:
    """Display available stock options and let user pick one or type a custom ticker."""
    print("\n" + "=" * 70)
    print("      INTELLIGENT FINANCIAL PLATFORM — 150 STOCKS MULTI-MARKET")
    print("=" * 70)
    print("  [1] BSE Sensex      (30 Stocks  — India, INR)")
    print("  [2] NSE Nifty 50    (50 Stocks  — India, INR)")
    print("  [3] Nasdaq-100      (100 Stocks — US, USD)")
    print("  [4] View All 150 Stocks")
    print("  [S] Search by company name or ticker")
    print("  [C] Custom ticker symbol")
    print("=" * 70)
    print("  Tip: You can also directly type any number (1-150) or ticker (e.g. TSLA, TCS.NS)")

    choice = input("\nSelect an index (1-4), [S]earch, [C]ustom, or type ticker/number: ").strip()

    # Direct ticker or number match
    if choice.isdigit() and choice in config.STOCK_OPTIONS:
        t, c, _ = config.STOCK_OPTIONS[choice]
        return t, c

    upper_choice = choice.upper()

    # Direct ticker string match across all options
    for k, (t, c, _) in config.STOCK_OPTIONS.items():
        if upper_choice == t.upper() or upper_choice == t.split(".")[0].upper():
            return t, c

    if choice == "1":
        _display_stock_grid(config.SENSEX_KEYS, "BSE Sensex Index")
        pick = input("\nEnter stock number (e.g., 1, 12) or ticker (default: 12 [TCS.NS]): ").strip()
        if pick in config.STOCK_OPTIONS:
            t, c, _ = config.STOCK_OPTIONS[pick]
            return t, c
        return config.STOCK_OPTIONS["12"][0], config.STOCK_OPTIONS["12"][1]

    elif choice == "2":
        _display_stock_grid(config.NIFTY_KEYS, "NSE Nifty 50 Index")
        pick = input("\nEnter stock number (1-50) or ticker (default: 1 [HDFCBANK.NS]): ").strip()
        if pick in config.STOCK_OPTIONS:
            t, c, _ = config.STOCK_OPTIONS[pick]
            return t, c
        return config.STOCK_OPTIONS["1"][0], config.STOCK_OPTIONS["1"][1]

    elif choice == "3":
        _display_stock_grid(config.NASDAQ_KEYS, "Nasdaq-100 Index")
        pick = input("\nEnter stock number (51-150) or ticker (default: 58 [TSLA]): ").strip()
        if pick in config.STOCK_OPTIONS:
            t, c, _ = config.STOCK_OPTIONS[pick]
            return t, c
        return config.STOCK_OPTIONS["58"][0], config.STOCK_OPTIONS["58"][1]

    elif choice == "4":
        _display_stock_grid(list(config.STOCK_OPTIONS.keys()), "All 150 Multi-Market Stocks")
        pick = input("\nEnter stock number (1-150) or ticker (default: 51 [NVDA]): ").strip()
        if pick in config.STOCK_OPTIONS:
            t, c, _ = config.STOCK_OPTIONS[pick]
            return t, c
        return config.STOCK_OPTIONS["51"][0], config.STOCK_OPTIONS["51"][1]

    elif upper_choice == "S":
        q = input("\nEnter search keyword (e.g. Tata, Adani, Apple, Bank): ").strip().lower()
        matches = [
            k for k, (t, c, cat) in config.STOCK_OPTIONS.items()
            if q in t.lower() or q in c.lower() or q in cat.lower()
        ]
        if matches:
            _display_stock_grid(matches, f"Search Results for '{q}'")
            pick = input(f"\nEnter stock number from results (default: {matches[0]}): ").strip()
            if pick in config.STOCK_OPTIONS:
                t, c, _ = config.STOCK_OPTIONS[pick]
                return t, c
            return config.STOCK_OPTIONS[matches[0]][0], config.STOCK_OPTIONS[matches[0]][1]
        else:
            print(f"No match found for '{q}'. Falling back to default.")

    elif upper_choice == "C":
        ticker = input("Enter custom ticker symbol (e.g., RELIANCE.NS, TSLA): ").strip().upper()
        company = input(f"Enter search name for news (e.g., Reliance Industries) [press enter for '{ticker}']: ").strip()
        return ticker, company or ticker

    # Fallback to TCS.NS
    return config.STOCK_OPTIONS["12"][0], config.STOCK_OPTIONS["12"][1]


def main():
    ticker, news_query = select_stock()
    print(f"\n=== Intelligent Financial Platform | {ticker} ({news_query}) ===\n")

    # --- [1/4] Sentiment Analysis ---
    print("-- [1/4] SENTIMENT ANALYSIS")
    headlines = fetch_headlines(query=news_query)
    results, sentiment_score = analyze_sentiment(headlines)
    print_sentiment_report(results, sentiment_score)
    plot_sentiment_distribution(results)

    # --- [2/4] Data & Features ---
    print("-- [2/4] DATA")
    raw_df = fetch_raw_data(ticker=ticker)
    df = engineer_features(raw_df, sentiment_score=sentiment_score)
    X_train, X_test, y_train, y_test, test_dates = train_test_split_df(df)

    # --- [3/4] Technical Analysis ---
    print("\n-- [3/4] TECHNICAL ANALYSIS")
    print_trend_summary(df, ticker=ticker)
    plot_moving_average(df, ticker=ticker)
    plot_bollinger_bands(df, ticker=ticker)

    # --- [4/4] Predictive Models ---
    print("\n-- [4/4] MODELS")
    # ----------------------------------------------------------
    # Model selection via command‑line argument
    # ----------------------------------------------------------
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--model", type=str, default="rf",
                        help="Model to run: rf, lstm, xgb, lgbm, catboost, gru, cnn_lstm, transformer, arima, svm")
    args, _ = parser.parse_known_args()
    model_name = args.model.lower()

    # -----------------------------------------------------------------
    # Map model names to objects implementing the BaseModel interface
    # -----------------------------------------------------------------
    from models.xgboost_model import XGBoostModel
    from models.lightgbm_model import LightGBMModel
    from models.catboost_model import CatBoostModel
    from models.gru_model import GRUModel
    from models.cnn_lstm_model import CNNLSTMModel
    from models.transformer_model import TransformerModel
    from models.arima_model import ARIMAModel
    from models.svm_model import SVMModel

    y_pred = None
    if model_name == "rf":
        print("\n  [4a] Random Forest")
        rf_model = train_random_forest(X_train, y_train)
        y_pred = rf_model.predict(X_test)
        plot_feature_importance(rf_model)
    elif model_name == "lstm":
        print("\n  [4b] LSTM (CUDA GPU Accelerated)")
        X_tr_s, X_te_s, y_tr_s, scaler_y = prepare_lstm_data(X_train, y_train, X_test)
        lstm_model, history = train_lstm(X_tr_s, y_tr_s)
        y_pred = predict_lstm(lstm_model, X_te_s, scaler_y)
        plot_training_loss(history)
    elif model_name == "xgb":
        print("\n  [4c] XGBoost")
        extra_model = XGBoostModel()
    elif model_name == "lgbm":
        print("\n  [4c] LightGBM")
        extra_model = LightGBMModel()
    elif model_name == "catboost":
        print("\n  [4c] CatBoost")
        extra_model = CatBoostModel()
    elif model_name == "gru":
        print("\n  [4c] GRU")
        extra_model = GRUModel()
    elif model_name == "cnn_lstm":
        print("\n  [4c] CNN‑LSTM")
        extra_model = CNNLSTMModel()
    elif model_name == "transformer":
        print("\n  [4c] Transformer")
        extra_model = TransformerModel()
    elif model_name == "arima":
        print("\n  [4c] ARIMA")
        extra_model = ARIMAModel()
    elif model_name == "svm":
        print("\n  [4c] SVM")
        extra_model = SVMModel()
    else:
        print(f"Unknown model '{model_name}'. Falling back to Random Forest.")
        extra_model = None
        model_name = "rf"
        rf_model = train_random_forest(X_train, y_train)
        y_pred = rf_model.predict(X_test)
        plot_feature_importance(rf_model)

    if extra_model is not None:
        print(f"\n  [4c] Training {extra_model.name()} model")
        extra_model.fit(X_train, y_train)
        y_pred = extra_model.predict(X_test)

    # ---------- Evaluation ----------
    print("\n-- EVALUATION")
    if model_name == "lstm":
        n = len(y_pred)
        y_test_eval = y_test[-n:]
        dates_eval = test_dates[-n:]
    else:
        y_test_eval = y_test
        dates_eval = test_dates
    metrics = compute_metrics(y_test_eval, y_pred)
    print_comparison_table(metrics, {}, ticker=ticker)
    plot_comparison(dates_eval, y_test_eval, y_pred, y_pred, ticker=ticker)

    print("\nDone!\n")

if __name__ == "__main__":
    main()
