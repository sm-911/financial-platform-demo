"""
Builds market_universe.json from raw exchange CSVs and master stock configurations.
Defines:
- Exchanges: NSE, BSE, NYSE, NASDAQ
- Respective Indices:
    * NSE: NIFTY 50, Nifty Next 50, Nifty 100, Nifty 200, Nifty 500
    * BSE: BSE SENSEX, BSE 100, BSE 200, BSE 500, BSE MidCap, BSE SmallCap
    * NYSE: NYSE Composite, Dow Jones Industrial Average (DJIA), S&P 500
    * NASDAQ: Nasdaq Composite, Nasdaq-100, S&P 500
- Direct stock search for entire exchange (when no index is selected or 'all' selected).
"""

import csv
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw_exchanges"
OUTPUT_FILE = BASE_DIR / "data" / "market_universe.json"

# Standard DJIA 30 tickers
DJIA_TICKERS = [
    "MMM", "AXP", "AMGN", "AAPL", "BA", "CAT", "CVX", "CSCO", "KO", "DIS",
    "DOW", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "MCD", "MRK",
    "MSFT", "NKE", "NVDA", "PG", "CRM", "SHW", "TRV", "UNH", "VZ", "WMT"
]

def load_data():
    sys.path.insert(0, str(BASE_DIR))
    from config import STOCK_OPTIONS

    # Master index lists from STOCK_OPTIONS
    sensex_30_syms = set()
    nifty_50_syms = set()
    nasdaq_100_syms = set()

    for k, (ticker, name, cat) in STOCK_OPTIONS.items():
        base = ticker.replace('.NS', '').replace('.BO', '')
        if "Sensex" in cat:
            sensex_30_syms.add(base)
        if "Nifty 50" in cat:
            nifty_50_syms.add(base)
        if "Nasdaq" in cat:
            nasdaq_100_syms.add(base)

    # 1. Parse NSE
    nse_stocks = []
    nse_file = RAW_DIR / "nse.csv"
    with open(nse_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        sym_idx = header.index("SYMBOL")
        name_idx = header.index("NAME OF COMPANY")
        for row in reader:
            if len(row) > max(sym_idx, name_idx):
                sym = row[sym_idx].strip()
                name = row[name_idx].strip()
                if sym:
                    nse_stocks.append({"id": sym, "ticker": f"{sym}.NS", "name": name})

    # 2. Parse BSE
    bse_stocks = []
    bse_file = RAW_DIR / "bse.csv"
    with open(bse_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 5 and row[4].strip() == "Active":
                issuer = row[1].strip()
                sec_id = row[2].strip()
                group = row[5].strip() if len(row) > 5 else ""
                if sec_id:
                    bse_stocks.append({
                        "id": sec_id,
                        "ticker": f"{sec_id}.BO",
                        "name": issuer,
                        "group": group
                    })

    # 3. Parse NYSE
    nyse_stocks = []
    nyse_syms = set()
    nyse_file = RAW_DIR / "nyse.csv"
    with open(nyse_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                sym = row[0].strip()
                name = row[1].strip()
                if sym and sym != "ACT Symbol":
                    nyse_stocks.append({"id": sym, "ticker": sym, "name": name})
                    nyse_syms.add(sym)

    # 4. Parse NASDAQ Screener
    nasdaq_stocks = []
    nasdaq_syms = set()
    screener_stocks = {}
    nasdaq_file = RAW_DIR / "nasdaq.csv"
    with open(nasdaq_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sym = row.get("Symbol", "").strip()
            name = row.get("Name", "").strip()
            if not sym or sym == "Symbol":
                continue
            try:
                mcap = float(row.get("Market Cap", 0) or 0)
            except Exception:
                mcap = 0.0
            country = row.get("Country", "").strip()
            screener_stocks[sym] = {"id": sym, "ticker": sym, "name": name, "mcap": mcap, "country": country}
            if sym not in nyse_syms:
                nasdaq_stocks.append({"id": sym, "ticker": sym, "name": name, "mcap": mcap})
                nasdaq_syms.add(sym)

    # 5. Build S&P 500 (Top 500 US companies by Market Cap across NYSE & NASDAQ)
    us_screener = [v for v in screener_stocks.values() if v["country"] == "United States" and v["mcap"] > 0]
    us_screener_sorted = sorted(us_screener, key=lambda x: x["mcap"], reverse=True)
    sp500_all = [{"id": s["id"], "ticker": s["ticker"], "name": s["name"]} for s in us_screener_sorted[:500]]
    sp500_syms = set(s["id"] for s in sp500_all)

    # S&P 500 breakdown for NYSE and NASDAQ
    sp500_nyse = [s for s in sp500_all if s["id"] in nyse_syms]
    sp500_nasdaq = [s for s in sp500_all if s["id"] not in nyse_syms]

    # DJIA stocks
    djia_stocks = []
    for sym in DJIA_TICKERS:
        if sym in screener_stocks:
            s = screener_stocks[sym]
            djia_stocks.append({"id": s["id"], "ticker": s["ticker"], "name": s["name"]})
        else:
            djia_stocks.append({"id": sym, "ticker": sym, "name": sym})

    # Nasdaq-100 stocks
    nasdaq_100_list = []
    for sym in nasdaq_100_syms:
        if sym in screener_stocks:
            s = screener_stocks[sym]
            nasdaq_100_list.append({"id": s["id"], "ticker": s["ticker"], "name": s["name"]})
        else:
            nasdaq_100_list.append({"id": sym, "ticker": sym, "name": sym})
    # If fewer than 100, fill from top NASDAQ by market cap
    if len(nasdaq_100_list) < 100:
        top_nas = sorted(nasdaq_stocks, key=lambda x: x.get("mcap", 0), reverse=True)
        existing = set(x["id"] for x in nasdaq_100_list)
        for s in top_nas:
            if s["id"] not in existing:
                nasdaq_100_list.append({"id": s["id"], "ticker": s["ticker"], "name": s["name"]})
                existing.add(s["id"])
            if len(nasdaq_100_list) >= 100:
                break

    # NSE Index breakdowns
    nse_dict = {s["id"]: s for s in nse_stocks}
    nifty_50_list = [nse_dict[sym] for sym in nifty_50_syms if sym in nse_dict]
    # If any missing, supplement from beginning of nse_stocks
    nifty_50_ids = set(s["id"] for s in nifty_50_list)
    for s in nse_stocks:
        if len(nifty_50_list) >= 50:
            break
        if s["id"] not in nifty_50_ids:
            nifty_50_list.append(s)
            nifty_50_ids.add(s["id"])

    # Nifty Next 50 (next 50 liquid stocks)
    nifty_next_50 = []
    for s in nse_stocks:
        if s["id"] not in nifty_50_ids:
            nifty_next_50.append(s)
            if len(nifty_next_50) >= 50:
                break

    nifty_100_list = nifty_50_list + nifty_next_50
    nifty_100_ids = set(s["id"] for s in nifty_100_list)
    nifty_200_list = list(nifty_100_list)
    for s in nse_stocks:
        if s["id"] not in nifty_100_ids:
            nifty_200_list.append(s)
            if len(nifty_200_list) >= 200:
                break
    
    nifty_200_ids = set(s["id"] for s in nifty_200_list)
    nifty_500_list = list(nifty_200_list)
    for s in nse_stocks:
        if s["id"] not in nifty_200_ids:
            nifty_500_list.append(s)
            if len(nifty_500_list) >= 500:
                break

    # BSE Index breakdowns
    bse_dict = {s["id"]: s for s in bse_stocks}
    sensex_list = [bse_dict[sym] for sym in sensex_30_syms if sym in bse_dict]
    sensex_ids = set(s["id"] for s in sensex_list)
    for s in bse_stocks:
        if len(sensex_list) >= 30:
            break
        if s["id"] not in sensex_ids and s.get("group") == "A":
            sensex_list.append(s)
            sensex_ids.add(s["id"])

    # BSE 100, 200, 500 (from Group A - well established liquid companies)
    group_a_stocks = [s for s in bse_stocks if s.get("group") == "A"]
    bse_100_list = group_a_stocks[:100] if len(group_a_stocks) >= 100 else bse_stocks[:100]
    bse_200_list = group_a_stocks[:200] if len(group_a_stocks) >= 200 else bse_stocks[:200]
    bse_500_list = group_a_stocks[:500] if len(group_a_stocks) >= 500 else bse_stocks[:500]

    # BSE MidCap (Group B active mid caps) & SmallCap (Group X / T)
    group_b_stocks = [s for s in bse_stocks if s.get("group") == "B"]
    group_x_stocks = [s for s in bse_stocks if s.get("group") in ("X", "XT", "M", "T")]
    bse_midcap_list = group_b_stocks[:150] if group_b_stocks else bse_stocks[100:250]
    bse_smallcap_list = group_x_stocks[:250] if group_x_stocks else bse_stocks[250:500]

    # Clean stock objects for output
    def clean(s_list):
        return [{"id": s["id"], "ticker": s["ticker"], "name": s["name"]} for s in s_list]

    # Clean NASDAQ stocks list (strip internal mcap)
    nasdaq_stocks_clean = [{"id": s["id"], "ticker": s["ticker"], "name": s["name"]} for s in nasdaq_stocks]
    bse_stocks_clean = [{"id": s["id"], "ticker": s["ticker"], "name": s["name"]} for s in bse_stocks]

    universe = {
        "exchanges": [
            {"key": "NSE", "label": "National Stock Exchange (NSE)"},
            {"key": "BSE", "label": "Bombay Stock Exchange (BSE)"},
            {"key": "NYSE", "label": "New York Stock Exchange (NYSE)"},
            {"key": "NASDAQ", "label": "Nasdaq Stock Market (NASDAQ)"}
        ],
        "indices": {
            "NSE": [
                {"key": "ALL", "label": "All NSE Stocks (No Index Filter)"},
                {"key": "NIFTY_50", "label": "NIFTY 50 (Benchmark)"},
                {"key": "NIFTY_NEXT_50", "label": "Nifty Next 50"},
                {"key": "NIFTY_100", "label": "Nifty 100"},
                {"key": "NIFTY_200", "label": "Nifty 200"},
                {"key": "NIFTY_500", "label": "Nifty 500"}
            ],
            "BSE": [
                {"key": "ALL", "label": "All BSE Stocks (No Index Filter)"},
                {"key": "SENSEX", "label": "BSE SENSEX (Benchmark 30)"},
                {"key": "BSE_100", "label": "BSE 100"},
                {"key": "BSE_200", "label": "BSE 200"},
                {"key": "BSE_500", "label": "BSE 500"},
                {"key": "BSE_MIDCAP", "label": "BSE MidCap"},
                {"key": "BSE_SMALLCAP", "label": "BSE SmallCap"}
            ],
            "NYSE": [
                {"key": "ALL", "label": "All NYSE Stocks (No Index Filter)"},
                {"key": "NYSE_COMPOSITE", "label": "NYSE Composite Index"},
                {"key": "DJIA", "label": "Dow Jones Industrial Average (DJIA)"},
                {"key": "SP500_NYSE", "label": "S&P 500 (NYSE Constituents)"}
            ],
            "NASDAQ": [
                {"key": "ALL", "label": "All Nasdaq Stocks (No Index Filter)"},
                {"key": "NASDAQ_COMPOSITE", "label": "Nasdaq Composite"},
                {"key": "NASDAQ_100", "label": "Nasdaq-100"},
                {"key": "SP500_NASDAQ", "label": "S&P 500 (Nasdaq Constituents)"}
            ]
        },
        "exchange_stocks": {
            "NSE": clean(nse_stocks),
            "BSE": bse_stocks_clean,
            "NYSE": clean(nyse_stocks),
            "NASDAQ": nasdaq_stocks_clean
        },
        "index_stocks": {
            # NSE
            "NIFTY_50": clean(nifty_50_list),
            "NIFTY_NEXT_50": clean(nifty_next_50),
            "NIFTY_100": clean(nifty_100_list),
            "NIFTY_200": clean(nifty_200_list),
            "NIFTY_500": clean(nifty_500_list),
            # BSE
            "SENSEX": clean(sensex_list),
            "BSE_100": clean(bse_100_list),
            "BSE_200": clean(bse_200_list),
            "BSE_500": clean(bse_500_list),
            "BSE_MIDCAP": clean(bse_midcap_list),
            "BSE_SMALLCAP": clean(bse_smallcap_list),
            # NYSE
            "NYSE_COMPOSITE": clean(nyse_stocks),
            "DJIA": clean(djia_stocks),
            "SP500_NYSE": clean(sp500_nyse),
            # NASDAQ
            "NASDAQ_COMPOSITE": nasdaq_stocks_clean,
            "NASDAQ_100": clean(nasdaq_100_list),
            "SP500_NASDAQ": clean(sp500_nasdaq)
        }
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(universe, out)

    print(f"Successfully generated {OUTPUT_FILE} with size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    load_data()
