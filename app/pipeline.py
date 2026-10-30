"""Pipeline orchestration used by the Flask web UI.

The heavy‑lifting (data fetch, sentiment, model training, plotting) lives here so the
HTTP request handler stays lightweight. All heavy work is run in a background thread
via :func:`app.cache_utils.run_background_task`.
"""
import io
import base64
import json
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Local imports – the project root is two levels up from this file.
import config
from data.stock_data import fetch_raw_data, engineer_features, train_test_split_df
from analysis.sentiment import fetch_headlines, analyze_sentiment, plot_sentiment_distribution
from analysis.technical import plot_moving_average, plot_bollinger_bands
from evaluation.compare_models import compute_metrics, plot_comparison

# Model imports (all follow the BaseModel interface)
from models.random_forest import train_random_forest, plot_feature_importance
from models.lstm_model import prepare_lstm_data, train_lstm, predict_lstm, plot_training_loss
from models.xgboost_model import XGBoostModel
from models.lightgbm_model import LightGBMModel
from models.catboost_model import CatBoostModel
from models.gru_model import GRUModel
from models.cnn_lstm_model import CNNLSTMModel
from models.transformer_model import TransformerModel
from models.arima_model import ARIMAModel
from models.svm_model import SVMModel

def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert a Matplotlib figure to a base64‑encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def _prepare_sequences(X, y, seq_len):
    """Utility for models that require a sliding‑window of *seq_len* steps.
    Returns ``X_seq`` (samples, seq_len, features) and ``y_seq`` (samples)."""
    xs, ys = [], []
    for i in range(len(X) - seq_len):
        xs.append(X[i : i + seq_len])
        ys.append(y[i + seq_len])
    return np.array(xs), np.array(ys)

def run_pipeline(ticker: str, news_query: str, selected_models: list, lookback: int = 60, horizon: int = 30, extra_params: dict = None):
    """Execute the full analysis for *ticker*.

    Returns a plain‑dictionary that can be JSON‑encoded and rendered in the Flask template.
    """
    extra_params = extra_params or {}

    # ---------- Sentiment ----------
    headlines = fetch_headlines(query=news_query)
    results, sentiment_score = analyze_sentiment(headlines)
    # Create the sentiment figure via the helper and encode it
    fig_sent = plot_sentiment_distribution(results)
    sentiment_img = _fig_to_base64(fig_sent)
    plt.close(fig_sent)

    # ---------- Data ----------
    raw_df = fetch_raw_data(ticker=ticker)
    df = engineer_features(raw_df, sentiment_score=sentiment_score)
    X_train, X_test, y_train, y_test, test_dates = train_test_split_df(df)

    # ---------- Technical plots ----------
    fig_ma = plot_moving_average(df, ticker=ticker)
    ma_img = _fig_to_base64(fig_ma)
    plt.close(fig_ma)

    fig_bb = plot_bollinger_bands(df, ticker=ticker)
    bb_img = _fig_to_base64(fig_bb)
    plt.close(fig_bb)

    # ---------- Model execution ----------
    model_results = []
    for model_name in selected_models:
        pred = None
        extra_img = None
        params = extra_params.get(model_name, {})
        if model_name == "rf":
            rf_model = train_random_forest(X_train, y_train)
            pred = rf_model.predict(X_test)
            # plot_feature_importance returns its own Figure
            fig_imp = plot_feature_importance(rf_model)
            extra_img = _fig_to_base64(fig_imp)
            plt.close(fig_imp)
        elif model_name == "lstm":
            X_tr_s, X_te_s, y_tr_s, scaler_y = prepare_lstm_data(X_train, y_train, X_test)
            lstm_model, history = train_lstm(X_tr_s, y_tr_s)
            pred = predict_lstm(lstm_model, X_te_s, scaler_y)
            # plot_training_loss returns its own Figure
            fig_loss = plot_training_loss(history)
            extra_img = _fig_to_base64(fig_loss)
            plt.close(fig_loss)
        elif model_name == "xgb":
            m = XGBoostModel(**params)
            m.fit(X_train, y_train)
            pred = m.predict(X_test)
        elif model_name == "lgbm":
            m = LightGBMModel(**params)
            m.fit(X_train, y_train)
            pred = m.predict(X_test)
        elif model_name == "catboost":
            m = CatBoostModel(**params)
            m.fit(X_train, y_train)
            pred = m.predict(X_test)
        elif model_name == "gru":
            m = GRUModel(**params)
            m.fit(X_train, y_train)
            pred = m.predict(X_test)
        elif model_name == "cnn_lstm":
            seq_len = lookback
            X_seq, y_seq = _prepare_sequences(X_train, y_train, seq_len)
            m = CNNLSTMModel(seq_len=seq_len, n_features=X_train.shape[1], **params)
            m.fit(X_seq, y_seq)
            X_test_seq, _ = _prepare_sequences(X_test, y_test, seq_len)
            pred = m.predict(X_test_seq)
        elif model_name == "transformer":
            seq_len = lookback
            X_seq, y_seq = _prepare_sequences(X_train, y_train, seq_len)
            m = TransformerModel(**params)
            m.fit(X_seq, y_seq)
            X_test_seq, _ = _prepare_sequences(X_test, y_test, seq_len)
            pred = m.predict(X_test_seq)
        elif model_name == "arima":
            m = ARIMAModel(**params)
            # ARIMA expects a 1‑D target series; we fit on the training target.
            m.fit(y_train)
            pred = m.predict(y_test, steps=len(y_test))
        elif model_name == "svm":
            m = SVMModel(**params)
            m.fit(X_train, y_train)
            pred = m.predict(X_test)
        else:
            continue

        # Align lengths for metric computation (some seq models truncate output)
        if pred is not None:
            if len(pred) != len(y_test):
                y_test_eff = y_test[-len(pred):]
                dates_eff = test_dates[-len(pred):]
            else:
                y_test_eff = y_test
                dates_eff = test_dates
            metrics = compute_metrics(y_test_eff, pred)
            # plot_comparison now returns its own Figure
            fig_cmp = plot_comparison(dates_eff, y_test_eff, pred, pred, ticker=ticker)
            cmp_img = _fig_to_base64(fig_cmp)
            plt.close(fig_cmp)
            model_results.append({
                "name": model_name,
                "metrics": metrics,
                "forecast_img": cmp_img,
                "extra_img": extra_img,
            })
    payload = {
        "ticker": ticker,
        "sentiment_img": sentiment_img,
        "ma_img": ma_img,
        "bb_img": bb_img,
        "model_results": model_results,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return payload
