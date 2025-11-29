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

def get_ticker_info(symbol: str) -> Dict:
    """
    Fetch detailed ticker info including volume, exchange, and institutional holders.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get institutional holders
        try:
            holders = ticker.institutional_holders
            if holders is not None and not holders.empty:
                top_holders = holders.head(3)['Holder'].tolist()
            else:
                top_holders = []
        except Exception:
            top_holders = []

        return {
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change_percent": info.get("regularMarketChangePercent") or 0.0,
            "volume": info.get("volume"),
            "average_volume": info.get("averageVolume"),
            "exchange": info.get("exchange"),
            "institutional_holders": top_holders,
            "insider_sentiment": "Neutral" # Placeholder, yfinance insider data is tricky to parse simply
        }
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return {}

def get_options_data(symbol: str) -> Optional[float]:
    """
    Calculate Put/Call Ratio from the nearest expiration option chain.
    """
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        if not expirations:
            return None
            
        # Get nearest expiration
        chain = ticker.option_chain(expirations[0])
        
        calls_vol = chain.calls['volume'].sum()
        puts_vol = chain.puts['volume'].sum()
        
        if calls_vol == 0:
            return None
            
        return round(puts_vol / calls_vol, 2)
    except Exception as e:
        print(f"Error fetching options for {symbol}: {e}")
        return None

def get_price_history(symbol: str, period: str = "1mo") -> List[Dict]:
    """
    Fetch historical price data for a ticker.
    Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    from datetime import datetime, timedelta
    import pandas as pd

    try:
        ticker = yf.Ticker(symbol)
        
        # Determine if we need intraday or daily
        if period in ["1d", "5d"]:
            # Intraday: No MAs for now (or could fetch daily separately, but keeping simple)
            interval = "15m" if period == "5d" else "5m"
            history = ticker.history(period=period, interval=interval)
            
            prices = []
            for index, row in history.iterrows():
                # Format date/time
                if interval in ["1m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                    time_str = index.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = index.strftime("%Y-%m-%d")
                    
                prices.append({
                    "time": time_str,
                    "price": round(row['Close'], 2),
                    "ma50": None,
                    "ma100": None,
                    "ema50": None,
                    "ema100": None
                })
            return prices
            
        else:
            # Daily: Fetch enough data for MAs
            # If user wants 1mo, we still need ~100 days prior for MA100.
            # So we fetch '2y' to be safe, unless they asked for 'max' or >2y.
            fetch_period = "2y"
            if period in ["5y", "10y", "max"]:
                fetch_period = period
            
            history = ticker.history(period=fetch_period, interval="1d")
            
            # Calculate MAs (Simple)
            history['MA50'] = history['Close'].rolling(window=50).mean()
            history['MA100'] = history['Close'].rolling(window=100).mean()
            
            # Calculate EMAs (Exponential)
            history['EMA50'] = history['Close'].ewm(span=50, adjust=False).mean()
            history['EMA100'] = history['Close'].ewm(span=100, adjust=False).mean()
            
            # Filter back to the requested period
            # Helper to filter by date
            cutoff_date = None
            now = datetime.now().astimezone(history.index.tz)
            
            if period == "1mo":
                cutoff_date = now - timedelta(days=30)
            elif period == "3mo":
                cutoff_date = now - timedelta(days=90)
            elif period == "6mo":
                cutoff_date = now - timedelta(days=180)
            elif period == "1y":
                cutoff_date = now - timedelta(days=365)
            elif period == "ytd":
                cutoff_date = datetime(now.year, 1, 1).astimezone(history.index.tz)
            # 2y, 5y, 10y, max: we already fetched what we need (or 2y is the fetch_period)
            
            if cutoff_date and period not in ["2y", "5y", "10y", "max"]:
                history = history[history.index >= cutoff_date]
            
            prices = []
            for index, row in history.iterrows():
                prices.append({
                    "time": index.strftime("%Y-%m-%d"),
                    "price": round(row['Close'], 2),
                    "ma50": round(row['MA50'], 2) if pd.notna(row['MA50']) else None,
                    "ma100": round(row['MA100'], 2) if pd.notna(row['MA100']) else None,
                    "ema50": round(row['EMA50'], 2) if pd.notna(row['EMA50']) else None,
                    "ema100": round(row['EMA100'], 2) if pd.notna(row['EMA100']) else None
                })
                
            return prices

    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return []
