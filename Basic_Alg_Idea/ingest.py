import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin

def get_sp500_tickers() -> list[str]:
    """
    Scrape the current list of S&P 500 tickers from Wikipedia.
    Returns a list of symbols with '.' replaced by '-' (e.g., BRK.B -> BRK-B).
    Falls back to a small default list on error.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        df = pd.read_html(url, header=0)[0]
        tickers = df['Symbol'].astype(str).str.replace('.', '-', regex=False).tolist()
        return tickers
    except Exception:
        # fallback to a few major tickers if scraping fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK-B', 'JNJ', 'V', 'WMT', 'JPM', 'META', 'NVDA', 'UNH', 'HD', 'PG', 'DIS', 'MA', 'PYPL', 'BAC']

def yfinance_scrape(tickers: list[str] | None = None, max_tickers: int | None = 500) -> list[dict]:
    """
    Scrape news headlines from Yahoo Finance for a list of stock tickers.

    Args:
        tickers: Optional list of tickers to scrape. If None, fetches S&P 500 tickers.
        max_tickers: Optional limit on how many tickers to process (default 500).

    Returns:
        List of dictionaries containing 'ticker' and 'headline'.
    """
    if tickers is None:
        tickers = get_sp500_tickers()

    if max_tickers is not None:
        tickers = tickers[:max_tickers]

    all_headlines = []
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; goodfellow-bot/0.1)'})

    for ticker in tickers:
        url = f"https://finance.yahoo.com/quote/{ticker}/news?p={ticker}"
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all news headlines
            headlines = soup.find_all('h3', class_='Mb(5px)')

            for headline in headlines:
                text = headline.get_text(strip=True)
                all_headlines.append({'ticker': ticker, 'headline': text})
        except Exception:
            # skip problematic tickers and continue
            continue

        # polite rate limiting to avoid hammering the site
        time.sleep(random.uniform(0.2, 0.8))

    return all_headlines

def yfinance_general_headlines(max_headlines: int = 200, sources: list[str] | None = None) -> list[dict]:
    """
    Fetch general market headlines from Yahoo Finance (not ticker-specific).

    Args:
        max_headlines: maximum number of headlines to return.
        sources: optional list of Yahoo Finance pages to scrape. If None, uses a sensible default.

    Returns:
        List of dicts: {'source': source_url, 'headline': text, 'link': absolute_url}
    """
    if sources is None:
        sources = [
            "https://finance.yahoo.com/",                       # front page / top stories
            "https://finance.yahoo.com/news",                   # news feed
            "https://finance.yahoo.com/topic/stock-market-news" # market-focused stories
        ]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; goodfellow-bot/0.1)'})

    results: list[dict] = []
    for source in sources:
        if len(results) >= max_headlines:
            break
        try:
            resp = session.get(source, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Try common headline containers: h3 or h2 elements with links
            candidates = []
            candidates += soup.find_all('h3')
            candidates += soup.find_all('h2')
            candidates += soup.find_all('a', {'class': 'Fw(600)'})  # sometimes used for headlines

            seen = set()
            for el in candidates:
                if len(results) >= max_headlines:
                    break
                # extract link and text
                link_tag = el.find('a') if el.name != 'a' else el
                text = el.get_text(strip=True)
                if not text:
                    continue
                href = link_tag.get('href') if link_tag is not None else None
                if href:
                    href = urljoin("https://finance.yahoo.com", href)
                # deduplicate similar headlines
                key = (text, href)
                if key in seen:
                    continue
                seen.add(key)
                results.append({'source': source, 'headline': text, 'link': href})
        except Exception:
            # ignore errors for a source and continue with others
            continue

        # polite delay
        time.sleep(random.uniform(0.3, 1.0))

    return results[:max_headlines]

# Example usage:
# if __name__ == "__main__":
#     headlines = yfinance_general_headlines(100)
#     for h in headlines[:10]:
#         print(h)