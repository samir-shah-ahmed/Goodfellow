import yfinance as yf
import pandas as pd
import time
import random
from typing import List, Dict, Optional

def get_sp500_tickers() -> List[str]:
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

def yfinance_scrape(tickers: Optional[List[str]] = None, max_tickers: Optional[int] = 500) -> List[Dict]:
    """
    Scrape news headlines from Yahoo Finance for a list of stock tickers using yfinance library.

    Args:
        tickers: Optional list of tickers to scrape. If None, fetches S&P 500 tickers.
        max_tickers: Optional limit on how many tickers to process (default 500).

    Returns:
        List of dictionaries containing 'ticker', 'headline', 'link', 'source', 'published_at'.
    """
    if tickers is None:
        tickers = get_sp500_tickers()

    if max_tickers is not None:
        tickers = tickers[:max_tickers]

    all_headlines = []

    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news
            
            for item in news:
                # Extract relevant fields from yfinance news object
                content = item.get('content', {})
                title = content.get('title')
                if not title:
                    continue
                    
                click_through_url = content.get('clickThroughUrl')
                link = click_through_url.get('url') if click_through_url else None
                
                provider = content.get('provider', {})
                source = provider.get('displayName')
                
                pub_date = content.get('pubDate')

                all_headlines.append({
                    'ticker': ticker_symbol, 
                    'headline': title,
                    'link': link,
                    'source': source,
                    'published_at': pub_date
                })
        except Exception as e:
            print(f"Error fetching news for {ticker_symbol}: {e}")
            continue

        # polite rate limiting (even with library, good practice)
        time.sleep(random.uniform(0.1, 0.3))

    return all_headlines

def yfinance_general_headlines(max_headlines: int = 200, sources: Optional[List[str]] = None) -> List[Dict]:
    """
    Fetch general market headlines. 
    Note: yfinance library is ticker-centric. For general news, we might need to rely on 
    major indices tickers like ^GSPC (S&P 500) or just return a mix of major tech news.
    For now, we'll fetch news for SPY (S&P 500 ETF) as a proxy for general market news.
    """
    return yfinance_scrape(tickers=['SPY', 'QQQ', 'DIA'], max_tickers=3)
