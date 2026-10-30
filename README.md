# 📈 Intelligent Financial Research & Analysis Platform

> *"An intelligent financial analysis platform that combines stock data, news sentiment, and Random Forest & LSTM models to help users analyze and understand stock market trends more efficiently."*

---

## 🔍 What It Does

| Step | What Happens |
|---|---|
| 1️⃣ News Sentiment | Fetches live headlines from NewsAPI, scores them with VADER NLP |
| 2️⃣ Stock Data | Downloads 2 years of OHLCV data via `yfinance` |
| 3️⃣ Technical Analysis | Plots Close Price + MA20 + Bollinger Bands, prints trend summary |
| 4️⃣ Random Forest | Trains a tree-based ML model; shows feature importance chart |
| 5️⃣ LSTM | Trains a neural network on 60-day price windows; plots loss curve |
| 6️⃣ Evaluation | Computes RMSE, MAE, R²; plots Actual vs Both Predictions |

---

## 📁 Project Structure

```
intelligent-financial-platform/
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
│   └── lstm_model.py              ← Keras LSTM model
│
├── evaluation/
│   └── compare_models.py          ← RMSE/MAE/R², comparison charts
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/intelligent-financial-platform.git
cd intelligent-financial-platform

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install all dependencies
pip install -r requirements.txt
```

---

## 🔑 NewsAPI Key (Optional but Recommended)

1. Go to [https://newsapi.org/register](https://newsapi.org/register) — free in 30 seconds.
2. Open `config.py` and replace:
   ```python
   NEWSAPI_KEY = "YOUR_NEWSAPI_KEY_HERE"
   ```
   with your actual key.

> Without a key, the platform uses a built-in set of fallback headlines — everything else still works.

---

## ▶️ Run

```bash
python main.py
```

**To change the stock**, edit `config.py`:
```python
TICKER      = "RELIANCE.NS"     # or "AAPL", "INFY.NS", etc.
NEWS_QUERY  = "Reliance Industries"
```

---

## 📊 Charts Produced

1. Close Price + 20-Day Moving Average
2. Bollinger Bands
3. News Sentiment Distribution (green/red/grey bar chart)
4. Random Forest Feature Importance
5. LSTM Training & Validation Loss Curve
6. Actual vs RF vs LSTM Prediction (line chart)
7. RMSE & MAE side-by-side bar chart

---

## 📐 Metrics Explained

| Metric | Meaning | Better when |
|---|---|---|
| **RMSE** | Avg. prediction error in ₹ (penalises large errors more) | Lower |
| **MAE** | Avg. absolute error in ₹ | Lower |
| **R²** | How much price variance the model explains (max = 1.0) | Higher |

---

## 🧰 Dependencies

| Package | Purpose |
|---|---|
| `yfinance` | Stock price data |
| `pandas`, `numpy` | Data manipulation |
| `matplotlib` | All charts |
| `nltk` | VADER sentiment analysis |
| `scikit-learn` | Random Forest, metrics, scaling |
| `tensorflow` | LSTM neural network |
| `requests` | NewsAPI HTTP calls |

---

## 📝 License

MIT
