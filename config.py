"""
=========================================================
  config.py
  ---------
  Single source of truth for all configurable settings.
  Comprehensive multi-market coverage:
    - BSE Sensex (30 stocks)
    - NSE Nifty 50 (50 stocks)
    - Nasdaq-100 (100 stocks)
=========================================================
"""

# ---------------------------------------------------------------------------
# Section 1 – Stock Settings & Master Universe
# ---------------------------------------------------------------------------
TICKER  = "TCS.NS"   # Default ticker symbol
PERIOD  = "2y"       # Data window — needs to be long for LSTM training

# 150 Pre-configured popular stocks with index classification and news search query
STOCK_OPTIONS = {
    "1": ("HDFCBANK.NS", "HDFC Bank", "Sensex, Nifty 50"),
    "2": ("ICICIBANK.NS", "ICICI Bank", "Sensex, Nifty 50"),
    "3": ("SBIN.NS", "State Bank of India", "Sensex, Nifty 50"),
    "4": ("KOTAKBANK.NS", "Kotak Mahindra Bank", "Sensex, Nifty 50"),
    "5": ("AXISBANK.NS", "Axis Bank", "Sensex, Nifty 50"),
    "6": ("BAJFINANCE.NS", "Bajaj Finance", "Sensex, Nifty 50"),
    "7": ("BAJAJFINSV.NS", "Bajaj Finserv", "Sensex, Nifty 50"),
    "8": ("RELIANCE.NS", "Reliance Industries", "Sensex, Nifty 50"),
    "9": ("NTPC.NS", "NTPC", "Sensex, Nifty 50"),
    "10": ("POWERGRID.NS", "Power Grid Corporation", "Sensex, Nifty 50"),
    "11": ("INFY.NS", "Infosys", "Sensex, Nifty 50"),
    "12": ("TCS.NS", "Tata Consultancy Services", "Sensex, Nifty 50"),
    "13": ("HCLTECH.NS", "HCL Technologies", "Sensex, Nifty 50"),
    "14": ("TECHM.NS", "Tech Mahindra", "Sensex, Nifty 50"),
    "15": ("MARUTI.NS", "Maruti Suzuki", "Sensex, Nifty 50"),
    "16": ("M&M.NS", "Mahindra & Mahindra", "Sensex, Nifty 50"),
    "17": ("HINDUNILVR.NS", "Hindustan Unilever", "Sensex, Nifty 50"),
    "18": ("ITC.NS", "ITC Limited", "Sensex, Nifty 50"),
    "19": ("TITAN.NS", "Titan Company", "Sensex, Nifty 50"),
    "20": ("TRENT.NS", "Trent", "Sensex, Nifty 50"),
    "21": ("SUNPHARMA.NS", "Sun Pharma", "Sensex, Nifty 50"),
    "22": ("TATASTEEL.NS", "Tata Steel", "Sensex, Nifty 50"),
    "23": ("LT.NS", "Larsen & Toubro", "Sensex, Nifty 50"),
    "24": ("ULTRACEMCO.NS", "UltraTech Cement", "Sensex, Nifty 50"),
    "25": ("ADANIPORTS.NS", "Adani Ports", "Sensex, Nifty 50"),
    "26": ("BEL.NS", "Bharat Electronics", "Sensex, Nifty 50"),
    "27": ("ASIANPAINT.NS", "Asian Paints", "Sensex, Nifty 50"),
    "28": ("INDIGO.NS", "InterGlobe Aviation IndiGo", "Sensex, Nifty 50"),
    "29": ("ZOMATO.NS", "Zomato Eternal", "Sensex, Nifty 50"),
    "30": ("BHARTIARTL.NS", "Bharti Airtel", "Sensex, Nifty 50"),
    "31": ("TATAMOTORS.NS", "Tata Motors", "Nifty 50"),
    "32": ("GRASIM.NS", "Grasim Industries", "Nifty 50"),
    "33": ("HINDALCO.NS", "Hindalco Industries", "Nifty 50"),
    "34": ("CIPLA.NS", "Cipla", "Nifty 50"),
    "35": ("DRREDDY.NS", "Dr Reddy Laboratories", "Nifty 50"),
    "36": ("COALINDIA.NS", "Coal India", "Nifty 50"),
    "37": ("EICHERMOT.NS", "Eicher Motors", "Nifty 50"),
    "38": ("APOLLOHOSP.NS", "Apollo Hospitals", "Nifty 50"),
    "39": ("HEROMOTOCO.NS", "Hero MotoCorp", "Nifty 50"),
    "40": ("JSWSTEEL.NS", "JSW Steel", "Nifty 50"),
    "41": ("ONGC.NS", "ONGC Oil and Natural Gas Corporation", "Nifty 50"),
    "42": ("ADANIENT.NS", "Adani Enterprises", "Nifty 50"),
    "43": ("BSE.NS", "BSE Limited", "Nifty 50"),
    "44": ("MAXHEALTH.NS", "Max Healthcare Institute", "Nifty 50"),
    "45": ("SHRIRAMFIN.NS", "Shriram Finance", "Nifty 50"),
    "46": ("TATACONSUM.NS", "Tata Consumer Products", "Nifty 50"),
    "47": ("HDFCLIFE.NS", "HDFC Life Insurance", "Nifty 50"),
    "48": ("SBILIFE.NS", "SBI Life Insurance", "Nifty 50"),
    "49": ("JIOFIN.NS", "Jio Financial Services", "Nifty 50"),
    "50": ("NESTLEIND.NS", "Nestle India", "Nifty 50"),
    "51": ("NVDA", "Nvidia", "Nasdaq-100"),
    "52": ("AAPL", "Apple", "Nasdaq-100"),
    "53": ("MSFT", "Microsoft", "Nasdaq-100"),
    "54": ("AMZN", "Amazon", "Nasdaq-100"),
    "55": ("GOOGL", "Alphabet Class A", "Nasdaq-100"),
    "56": ("GOOG", "Alphabet Class C", "Nasdaq-100"),
    "57": ("META", "Meta Platforms", "Nasdaq-100"),
    "58": ("TSLA", "Tesla", "Nasdaq-100"),
    "59": ("AVGO", "Broadcom", "Nasdaq-100"),
    "60": ("COST", "Costco Wholesale", "Nasdaq-100"),
    "61": ("NFLX", "Netflix", "Nasdaq-100"),
    "62": ("AMD", "Advanced Micro Devices", "Nasdaq-100"),
    "63": ("PEP", "PepsiCo", "Nasdaq-100"),
    "64": ("TMUS", "T-Mobile US", "Nasdaq-100"),
    "65": ("CSCO", "Cisco Systems", "Nasdaq-100"),
    "66": ("ADBE", "Adobe", "Nasdaq-100"),
    "67": ("QCOM", "Qualcomm", "Nasdaq-100"),
    "68": ("INTC", "Intel", "Nasdaq-100"),
    "69": ("INTU", "Intuit", "Nasdaq-100"),
    "70": ("TXN", "Texas Instruments", "Nasdaq-100"),
    "71": ("AMGN", "Amgen", "Nasdaq-100"),
    "72": ("PANW", "Palo Alto Networks", "Nasdaq-100"),
    "73": ("HON", "Honeywell International", "Nasdaq-100"),
    "74": ("AMAT", "Applied Materials", "Nasdaq-100"),
    "75": ("BKNG", "Booking Holdings", "Nasdaq-100"),
    "76": ("VRTX", "Vertex Pharmaceuticals", "Nasdaq-100"),
    "77": ("MDLZ", "Mondelez International", "Nasdaq-100"),
    "78": ("ADP", "Automatic Data Processing", "Nasdaq-100"),
    "79": ("ADI", "Analog Devices", "Nasdaq-100"),
    "80": ("LOW", "Lowe's Companies", "Nasdaq-100"),
    "81": ("CMCSA", "Comcast", "Nasdaq-100"),
    "82": ("ISRG", "Intuitive Surgical", "Nasdaq-100"),
    "83": ("LRCX", "Lam Research", "Nasdaq-100"),
    "84": ("REGN", "Regeneron Pharmaceuticals", "Nasdaq-100"),
    "85": ("GILD", "Gilead Sciences", "Nasdaq-100"),
    "86": ("PNRA", "Panera Bread", "Nasdaq-100"),
    "87": ("SBUX", "Starbucks", "Nasdaq-100"),
    "88": ("CMG", "Chipotle Mexican Grill", "Nasdaq-100"),
    "89": ("MELI", "MercadoLibre", "Nasdaq-100"),
    "90": ("MRVL", "Marvell Technology", "Nasdaq-100"),
    "91": ("PCAR", "PACCAR", "Nasdaq-100"),
    "92": ("SNPS", "Synopsys", "Nasdaq-100"),
    "93": ("CDNS", "Cadence Design Systems", "Nasdaq-100"),
    "94": ("WDAY", "Workday", "Nasdaq-100"),
    "95": ("ASML", "ASML Holding", "Nasdaq-100"),
    "96": ("PLTR", "Palantir Technologies", "Nasdaq-100"),
    "97": ("CRWD", "CrowdStrike", "Nasdaq-100"),
    "98": ("ABNB", "Airbnb", "Nasdaq-100"),
    "99": ("MAR", "Marriott International", "Nasdaq-100"),
    "100": ("PAYX", "Paychex", "Nasdaq-100"),
    "101": ("LULU", "Lululemon Athletica", "Nasdaq-100"),
    "102": ("ADSK", "Autodesk", "Nasdaq-100"),
    "103": ("DDOG", "Datadog", "Nasdaq-100"),
    "104": ("FTNT", "Fortinet", "Nasdaq-100"),
    "105": ("ODFL", "Old Dominion Freight Line", "Nasdaq-100"),
    "106": ("CTSH", "Cognizant Technology Solutions", "Nasdaq-100"),
    "107": ("SPCX", "SpaceX", "Nasdaq-100"),
    "108": ("EW", "Edwards Lifesciences", "Nasdaq-100"),
    "109": ("DXCM", "DexCom", "Nasdaq-100"),
    "110": ("IDXX", "Idexx Laboratories", "Nasdaq-100"),
    "111": ("MNST", "Monster Beverage", "Nasdaq-100"),
    "112": ("KDP", "Keurig Dr Pepper", "Nasdaq-100"),
    "113": ("CSGP", "CoStar Group", "Nasdaq-100"),
    "114": ("VRSK", "Verisk Analytics", "Nasdaq-100"),
    "115": ("EA", "Electronic Arts", "Nasdaq-100"),
    "116": ("FAST", "Fastenal", "Nasdaq-100"),
    "117": ("BIIB", "Biogen", "Nasdaq-100"),
    "118": ("ANSS", "Ansys", "Nasdaq-100"),
    "119": ("MCHP", "Microchip Technology", "Nasdaq-100"),
    "120": ("WBA", "Walgreens Boots Alliance", "Nasdaq-100"),
    "121": ("WBD", "Warner Bros. Discovery", "Nasdaq-100"),
    "122": ("DLTR", "Dollar Tree", "Nasdaq-100"),
    "123": ("SIRI", "Sirius XM", "Nasdaq-100"),
    "124": ("EBAY", "eBay", "Nasdaq-100"),
    "125": ("ZM", "Zoom Video Communications", "Nasdaq-100"),
    "126": ("ZS", "Zscaler", "Nasdaq-100"),
    "127": ("TMV.DE", "TeamViewer", "Nasdaq-100"),
    "128": ("SHOP", "Shopify", "Nasdaq-100"),
    "129": ("ARM", "Arm Holdings", "Nasdaq-100"),
    "130": ("DG", "Dollar General", "Nasdaq-100"),
    "131": ("BKR", "Baker Hughes", "Nasdaq-100"),
    "132": ("CEG", "Constellation Energy", "Nasdaq-100"),
    "133": ("FANG", "Diamondback Energy", "Nasdaq-100"),
    "134": ("EXC", "Exelon Corporation", "Nasdaq-100"),
    "135": ("AEP", "American Electric Power", "Nasdaq-100"),
    "136": ("XEL", "Xcel Energy", "Nasdaq-100"),
    "137": ("ED", "Consolidated Edison", "Nasdaq-100"),
    "138": ("PEG", "Public Service Enterprise Group", "Nasdaq-100"),
    "139": ("ROP", "Roper Technologies", "Nasdaq-100"),
    "140": ("CPRT", "Copart", "Nasdaq-100"),
    "141": ("FSLY", "Fastly", "Nasdaq-100"),
    "142": ("NET", "Cloudflare", "Nasdaq-100"),
    "143": ("HUBS", "HubSpot", "Nasdaq-100"),
    "144": ("SNOW", "Snowflake", "Nasdaq-100"),
    "145": ("MDB", "MongoDB", "Nasdaq-100"),
    "146": ("PINS", "Pinterest", "Nasdaq-100"),
    "147": ("SNAP", "Snap Inc", "Nasdaq-100"),
    "148": ("TTD", "Trade Desk", "Nasdaq-100"),
    "149": ("SPLK", "Splunk", "Nasdaq-100"),
    "150": ("TTWO", "Take-Two Interactive", "Nasdaq-100"),
}

# Convenience index filter groupings
SENSEX_KEYS   = [k for k, v in STOCK_OPTIONS.items() if "Sensex" in v[2]]
NIFTY_KEYS    = [k for k, v in STOCK_OPTIONS.items() if "Nifty 50" in v[2]]
NASDAQ_KEYS   = [k for k, v in STOCK_OPTIONS.items() if "Nasdaq-100" in v[2]]

# ---------------------------------------------------------------------------
# Section 2 – Technical Analysis Settings
# ---------------------------------------------------------------------------
MA_WINDOW = 20       # Days for simple moving average

# ---------------------------------------------------------------------------
# Section 3 – News / Sentiment Settings
# ---------------------------------------------------------------------------
NEWSAPI_KEY   = "72e1ccfdb2d7409e90f82a7e0011ae22"
NEWS_QUERY    = None    # None = auto-derived from TICKER
NEWS_MAX      = 10      # Max headlines to fetch & analyse

# ---------------------------------------------------------------------------
# Section 4 – Random Forest Settings
# ---------------------------------------------------------------------------
RF_N_ESTIMATORS = 200    # Number of decision trees
RF_MAX_DEPTH    = None   # None = nodes expand until pure
RF_RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# Section 5 – LSTM Settings
# ---------------------------------------------------------------------------
LSTM_LOOKBACK   = 60     # Days of history fed into each LSTM input window
LSTM_UNITS      = 64     # Neurons in the LSTM layer
LSTM_DROPOUT    = 0.2    # Dropout rate
LSTM_EPOCHS     = 50
LSTM_BATCH_SIZE = 32

# ---------------------------------------------------------------------------
# Section 6 – Train / Test Split
# ---------------------------------------------------------------------------
TEST_SPLIT = 0.2         # 20% of data held out for evaluation
