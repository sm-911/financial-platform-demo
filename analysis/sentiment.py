"""Sentiment analysis: fetch headlines (NewsAPI or stock-tailored fallback), score with VADER, plot."""

import requests
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.ticker_lookup import get_company_name


def generate_stock_headlines(ticker_or_query: str = None) -> list[str]:
    """Generate six dynamic, ticker-specific financial headlines used as fallback.

    Accepts either a raw ticker (e.g. 'AAPL', 'TCS.NS') or a company-name
    query string (e.g. 'Apple Inc').  Company name is resolved via
    ticker_lookup so headlines always mention the real company name.
    """
    raw = (ticker_or_query or config.TICKER).strip()

    # Try to resolve via ticker map first (works for pure ticker strings like 'AAPL', 'TCS.NS')
    company = get_company_name(raw)

    # If get_company_name() returned the same value (ticker not found in map),
    # the caller may have passed a company-name string directly (e.g. "Apple Inc").
    # In that case keep the original (human-readable) string rather than uppercasing it.
    if company.upper() == raw.upper():
        company = raw  # preserve original casing of the query string

    # Extra cleanup: strip common legal suffixes that sneak through when the
    # caller passes a company-name string (e.g. "Apple Inc", "Reliance Industries")
    for suffix in [" Inc", " Inc.", " Corporation", " Corp", " Corp.",
                   " Limited", " Ltd", " Ltd.", " Industries", " Bank",
                   " Services", " Technologies"]:
        if company.lower().endswith(suffix.lower()):
            company = company[: -len(suffix)].strip()
            break

    return [
        f"{company} reports strong quarterly revenue and profit growth",
        f"{company} faces short-term market headwinds and rising operational costs",
        f"{company} signs major global partnership to expand its solutions",
        f"{company} strengthens foothold across new international growth markets",
        f"{company} announces strategic share buyback and capital return plan",
        f"{company} earnings meet institutional expectations amid sector volatility",
    ]


def fetch_headlines(query: str = None,
                    api_key: str = config.NEWSAPI_KEY,
                    max_articles: int = config.NEWS_MAX) -> list[str]:
    """Return headlines from NewsAPI, falling back to stock-personalised headlines on any failure.

    If *query* is None (or config.NEWS_QUERY is None), the company name is
    auto-derived from config.TICKER via ticker_lookup, so searches are always
    meaningful (e.g. "Apple" not "AAPL").
    """
    # Resolve query: prefer caller-supplied > config > auto-derive from ticker
    raw_query = query or config.NEWS_QUERY
    if not raw_query:
        raw_query = get_company_name(config.TICKER)  # e.g. "Apple", "Tata Consultancy Services"

    # For short single-word company names (e.g. "Apple", "Tesla") NewsAPI returns
    # many off-topic articles.  Appending "stock" narrows results to financial news.
    search_query = raw_query
    if len(raw_query.split()) <= 2 and "stock" not in raw_query.lower():
        search_query = raw_query + " stock"

    # Fallback headlines always use the same resolved name
    fallback_news = generate_stock_headlines(raw_query)

    if api_key == "YOUR_NEWSAPI_KEY_HERE" or not api_key:
        print(f"  * No NewsAPI key — using personalised fallback headlines for '{raw_query}'.")
        return fallback_news[:max_articles]
    try:
        resp = requests.get("https://newsapi.org/v2/everything", timeout=10, params={
            "q": search_query, "language": "en", "sortBy": "publishedAt",
            "pageSize": max_articles, "apiKey": api_key,
        })
        resp.raise_for_status()
        headlines = [a["title"] for a in resp.json().get("articles", []) if a.get("title")]
        if not headlines:
            raise ValueError("0 articles returned by NewsAPI")
        print(f"  * {len(headlines)} live headlines fetched from NewsAPI for '{search_query}'.")
        return headlines
    except Exception as e:
        print(f"  * NewsAPI unavailable ({e}) — using personalised fallback headlines for '{raw_query}'.")
        return fallback_news[:max_articles]


def analyze_sentiment(headlines: list[str]) -> tuple[list[tuple], float]:
    """Score each headline with VADER. Returns (results, composite_score)."""
    import nltk
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()
    results = []
    for h in headlines:
        c = sia.polarity_scores(h)["compound"]
        label = "Positive" if c > 0.05 else "Negative" if c < -0.05 else "Neutral"
        results.append((h, c, label))
    composite = sum(r[1] for r in results) / len(results) if results else 0.0
    return results, composite


def print_sentiment_report(results: list[tuple], composite: float):
    EMOJI = {"Positive": "[+]", "Negative": "[-]", "Neutral": "[~]"}
    print(f"\n{'-'*60}\n  News Sentiment Analysis Report\n{'-'*60}")
    for h, score, label in results:
        print(f"  {EMOJI[label]} [{label:8s}] ({score:+.3f})  {h}")
    overall = "Positive" if composite > 0.05 else "Negative" if composite < -0.05 else "Neutral"
    print(f"{'-'*60}\n  Overall Sentiment: {overall}  (Average Compound = {composite:+.3f})\n{'-'*60}\n")


def plot_sentiment_distribution(results: list[tuple]):
    """Create a larger bar chart of sentiment distribution and return the Figure.
    The caller is responsible for encoding to base64; we do NOT call plt.show().
    """
    labels = [r[2] for r in results]
    counts = {
        "Positive": labels.count("Positive"),
        "Negative": labels.count("Negative"),
        "Neutral":  labels.count("Neutral"),
    }
    colors = {"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#9E9E9E"}
    fig, ax = plt.subplots(figsize=(10, 5))  # larger width for readability
    bars = ax.bar(counts.keys(), counts.values(),
                  color=[colors[k] for k in counts], edgecolor="white")
    for bar, val in zip(bars, counts.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_title("News Sentiment Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Headlines")
    ax.set_ylim(0, max(counts.values()) + 1.5)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig
    """Create a bar chart of sentiment distribution.
    Returns the Figure so caller can encode it; does NOT call plt.show().
    """
    labels = [r[2] for r in results]
    counts = {
        "Positive": labels.count("Positive"),
        "Negative": labels.count("Negative"),
        "Neutral":  labels.count("Neutral"),
    }
    colors = {"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#9E9E9E"}
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(counts.keys(), counts.values(),
                  color=[colors[k] for k in counts], edgecolor="white")
    for bar, val in zip(bars, counts.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_title("News Sentiment Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Headlines")
    ax.set_ylim(0, max(counts.values()) + 1.5)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig
    labels = [r[2] for r in results]
    counts = {
        "Positive": labels.count("Positive"),
        "Negative": labels.count("Negative"),
        "Neutral":  labels.count("Neutral"),
    }
    colors = {"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#9E9E9E"}
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(counts.keys(), counts.values(),
                  color=[colors[k] for k in counts], edgecolor="white")
    for bar, val in zip(bars, counts.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_title("News Sentiment Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Headlines")
    ax.set_ylim(0, max(counts.values()) + 1.5)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()
