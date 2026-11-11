# Intelligent Financial Research & Analysis Platform

> *"An intelligent financial analysis platform that combines global stock data, news sentiment, and a suite of machine‑learning models to help users analyze and understand stock market trends more efficiently."*

---

## Key Features

- **Multi-Exchange Support:** Browse and search securities across major global exchanges:
  - **NSE** (*National Stock Exchange of India*)
  - **BSE** (*Bombay Stock Exchange*)
  - **NYSE** (*New York Stock Exchange*)
  - **NASDAQ** (*Nasdaq Stock Market*)
- **Benchmark & Broad Market Indices:** Filter constituent stocks by benchmark indices:
  - **NSE:** NIFTY 50, Nifty Next 50, Nifty 100, Nifty 200, Nifty 500
  - **BSE:** BSE SENSEX, BSE 100, BSE 200, BSE 500, BSE MidCap, BSE SmallCap
  - **NYSE:** NYSE Composite, Dow Jones Industrial Average (DJIA), S&P 500
  - **NASDAQ:** Nasdaq Composite, Nasdaq-100, S&P 500
  - *Direct exchange search:* Option to search across all exchange stocks without an index filter.
- **Smart Autocomplete:** Instant, keyboard-navigable autocomplete search for both indices and stock tickers/company names.
- **News Sentiment Analysis:** Real-time headline fetching from NewsAPI scored with VADER NLP.
- **Technical Analysis:** Interactive charts for Close Price, MA20, and Bollinger Bands with automatic trend summaries.
- **10 Machine Learning & Deep Learning Models:** Train, evaluate, and compare:
  - Tree-based: **Random Forest**, **XGBoost**, **LightGBM**, **CatBoost**
  - Deep Learning / Neural: **LSTM**, **GRU**, **CNN‑LSTM**, **Transformer**
  - Statistical & Classical: **ARIMA**, **SVM**
- **Evaluation & Visual Comparison:** Side-by-side performance metrics (RMSE, MAE, MAPE, R²) and Actual vs. Predicted plots.

---

## Project Structure

```
financial-platform-demo/
│
├── run_app.py                     ← Web app server entry point
├── main.py                        ← CLI / standalone execution
├── config.py                      ← Settings, default ticker, options
│
├── app/                           ← Flask application
│   ├── routes.py                  ← Web routes & search APIs
│   ├── pipeline.py                ← Orchestration pipeline
│   ├── templates/                 ← HTML templates (index, waiting, result)
│   └── static/                    ← Styles & frontend JavaScript
│
├── data/
│   ├── build_market_universe.py   ← Generates unified market index & stocks
│   ├── market_universe.json       ← Indexed exchanges, indices & constituents
│   ├── raw_exchanges/             ← Exchange datasets (NSE, BSE, NYSE, NASDAQ)
│   └── stock_data.py              ← yfinance fetcher + feature engineering
│
├── analysis/
│   ├── technical.py               ← Moving averages, Bollinger Bands
│   └── sentiment.py               ← NewsAPI fetch + VADER sentiment analysis
│
├── models/                        ← Model implementations (RF, LSTM, XGB, etc.)
├── evaluation/                    ← Performance comparison & metric charts
│
├── requirements.txt               ← Python dependencies
├── Procfile                       ← Deployment process command for Render
├── render.yaml                    ← Blueprint configuration for Render
└── README.md
```

---

## Local Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/sm-911/financial-platform-demo.git
cd financial-platform-demo
```

### 2. Set up virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Web Application
```bash
python run_app.py
```

## Evaluation Metrics

| Metric | Name | Interpretation |
|---|---|---|
| **RMSE** | Root Mean Squared Error | Standard deviation of residuals; penalises large forecasting mistakes. Lower is better. |
| **MAE** | Mean Absolute Error | Average magnitude of errors. Lower is better. |
| **MAPE** | Mean Absolute Percentage Error | Percentage error relative to actual stock prices. Lower is better. |
| **R²** | Coefficient of Determination | Proportion of variance explained by model (max 1.0). Higher is better. |

---

## License
This project is licensed under the [MIT License](LICENSE).
