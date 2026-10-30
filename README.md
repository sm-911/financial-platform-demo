# 📈 Intelligent Financial Research & Analysis Platform

> *"An intelligent financial analysis platform that combines stock data, news sentiment, and a suite of machine‑learning models to help users analyze and understand stock market trends more efficiently."*

---

## 🔍 What It Does

| Step | What Happens |
|---|---|
| 1️⃣ News Sentiment | Fetches live headlines from NewsAPI, scores them with VADER NLP |
| 2️⃣ Stock Data | Downloads 2 years of OHLCV data via `yfinance` |
| 3️⃣ Technical Analysis | Plots Close Price + MA20 + Bollinger Bands, prints trend summary |
| 4️⃣ Machine Learning Models | Trains and evaluates a variety of models (Random Forest, XGBoost, LightGBM, CatBoost, GRU, CNN‑LSTM, Transformer, ARIMA, SVM, LSTM) and shows relevant charts |
| 5️⃣ Evaluation | Computes RMSE, MAE, MAPE, R²; plots Actual vs Predictions for each model |

---

## 📁 Project Structure

```
intelligent-financial-platform-expanded/
│
├── main.py                        ← Run this
├── config.py                      ← Change ticker/settings here
│
├── data/
│   └── stock_data.py              ← yfinance fetch + feature engineering
│
├── analysis/
│   ├── technical.py               ← MA chart, Bollinger Bands, trend summary
│   └── sentiment.py               ← NewsAPI fetch + VADER scoring + chart
│
├── models/
│   ├── random_forest.py           ← Random Forest regression
│   ├── xgboost_model.py           ← XGBoost regression
│   ├── lightgbm_model.py          ← LightGBM regression
│   ├── catboost_model.py          ← CatBoost regression
│   ├── gru_model.py               ← GRU recurrent network
│   ├── cnn_lstm_model.py          ← CNN‑LSTM hybrid network
│   ├── transformer_model.py       ← Transformer‑based time‑series model
│   ├── arima_model.py             ← Classical ARIMA model
│   ├── svm_model.py               ← Support Vector Regression
│   └── lstm_model.py              ← LSTM neural network
│
├── evaluation/
│   └── compare_models.py          ← RMSE/MAE/MAPE/R², comparison charts
│
├── app/                           ← Flask web UI (routes, pipeline, templates, static assets)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/sm-911/financial-platform-demo.git
cd financial-platform-demo

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # macOS / Linux

# 3. Install all dependencies
pip install -r requirements.txt
```

---

## 🔑 NewsAPI Key (Optional but Recommended)

1. Go to <https://newsapi.org/register> — free in 30 seconds.
2. Open `config.py` and replace:
   ```python
   NEWSAPI_KEY = "YOUR_NEWSAPI_KEY_HERE"
   ```
   with your actual key.

> Without a key, the platform uses a built‑in set of fallback headlines — everything else still works.

---

## ▶️ Run

```bash
python main.py
```

**To change the stock**, edit `config.py`:
```python
TICKER      = "RELIANCE.NS"   # or "AAPL", "INFY.NS", etc.
NEWS_QUERY  = "Reliance Industries"
```

---

## 📊 Charts Produced

1. Close Price + 20‑Day Moving Average
2. Bollinger Bands
3. News Sentiment Distribution (green/red/grey bar chart)
4. Feature Importance for each tree‑based model (Random Forest, XGBoost, LightGBM, CatBoost)
5. Training & Validation Loss Curves for LSTM, GRU, CNN‑LSTM, Transformer
6. Actual vs Predicted for every model (line chart)
7. RMSE, MAE, MAPE side‑by‑side bar chart for all models

---

## 📐 Metrics Explained

| Metric | Meaning | Better when |
|---|---|---|
| **RMSE** | Avg. prediction error (penalises large errors) | Lower |
| **MAE** | Avg. absolute error | Lower |
| **MAPE** | Mean absolute percentage error | Lower |
| **R²** | Proportion of variance explained (max = 1.0) | Higher |

---

## 🧰 Dependencies

| Package | Purpose |
|---|---|
| `yfinance` | Stock price data |
| `pandas`, `numpy` | Data manipulation |
| `matplotlib` | All charts |
| `nltk` | VADER sentiment analysis |
| `scikit-learn` | Random Forest, XGBoost, LightGBM, CatBoost, SVM, metrics, scaling |
| `tensorflow` | LSTM, GRU, CNN‑LSTM, Transformer |
| `requests` | NewsAPI HTTP calls |

---

## 📝 License
## 🧪 Testing & Contributions
We welcome **testing** of the platform and any **suggested edits**. Feel free to:
- Run the Jupyter notebook or the web UI and report any bugs or visual issues.
- Propose improvements to model selection, chart layouts, or documentation.
- Open a Pull Request with your changes – we’ll review and merge helpful contributions.
Your feedback helps make the platform more robust and user‑friendly.
MIT
