from fastapi import APIRouter, HTTPException
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
from app.models.schemas import TickerBrief, AnalyzedArticle, SentimentResult, PricePoint
from app.services.ingest import (
    yfinance_scrape, get_sp500_tickers, fetch_news_for_ticker,
    get_ticker_info, get_options_data, get_price_history
)
from app.services.classifier import analyze_sentiment
from app.services.sentiment_social import get_retail_sentiment
from app.services.insider import get_corporate_insiders
from app.services.politician import get_politician_trades

router = APIRouter()

# --- Caching Configuration ---
# Cache up to 100 tickers for 5 minutes (300 seconds)
ticker_cache = TTLCache(maxsize=100, ttl=300)

# ThreadPool for blocking I/O calls
executor = ThreadPoolExecutor(max_workers=10)

async def run_sync(func, *args):
    """Run a synchronous blocking function in a separate thread."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

@router.get("/ticker/{symbol}", response_model=TickerBrief)
async def get_ticker_brief(symbol: str):
    """
    Get a balanced brief for a specific ticker.
    Uses caching and parallel execution for sub-30ms hot path.
    """
    symbol = symbol.upper()

    # Check Cache
    if symbol in ticker_cache:
        return ticker_cache[symbol]

    # --- Parallel Fetching of Data ---
    # We fetch all independent data points concurrently
    
    # Define tasks
    news_task = run_sync(fetch_news_for_ticker, symbol)
    info_task = run_sync(get_ticker_info, symbol)
    options_task = run_sync(get_options_data, symbol)
    retail_task = run_sync(get_retail_sentiment, symbol)
    insider_task = run_sync(get_corporate_insiders, symbol)
    politician_task = run_sync(get_politician_trades, symbol)

    # Execute all tasks
    results = await asyncio.gather(
        news_task, info_task, options_task, retail_task, insider_task, politician_task
    )
    
    # Unpack results
    articles_data, ticker_info, put_call_ratio, retail_sent, corp_insiders, pol_trades = results

    # --- Process News & Sentiment ---
    analyzed_articles = []
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0

    if articles_data:
        # Create tasks for all sentiment analysis in parallel
        sentiment_tasks = [run_sync(analyze_sentiment, art['headline']) for art in articles_data]
        sentiment_results = await asyncio.gather(*sentiment_tasks)

        for art, (stance, confidence) in zip(articles_data, sentiment_results):
            text = art['headline']
            
            sentiment = SentimentResult(stance=stance, confidence=confidence)
            analyzed_article = AnalyzedArticle(
                headline=text,
                ticker=symbol,
                sentiment=sentiment,
                link=art.get('link')
            )
            analyzed_articles.append(analyzed_article)

            if stance == 'positive':
                bullish_count += 1
            elif stance == 'negative':
                bearish_count += 1
            else:
                neutral_count += 1

    # --- Calculate Safety Score ---
    total = bullish_count + bearish_count + neutral_count
    if total == 0:
        safety_score = 0.5
    else:
        score = (bullish_count * 1.0 + neutral_count * 0.5 + bearish_count * 0.0) / total
        safety_score = round(score, 2)

    # --- Construct Response ---
    brief = TickerBrief(
        symbol=symbol,
        bullish_count=bullish_count,
        bearish_count=bearish_count,
        neutral_count=neutral_count,
        articles=analyzed_articles,
        safety_score=safety_score,
        price=ticker_info.get("price"),
        change_percent=ticker_info.get("change_percent"),
        volume=ticker_info.get("volume"),
        average_volume=ticker_info.get("average_volume"),
        exchange=ticker_info.get("exchange"),
        institutional_holders=ticker_info.get("institutional_holders", []),
        insider_sentiment=ticker_info.get("insider_sentiment"),
        put_call_ratio=put_call_ratio,
        retail_sentiment=retail_sent or "Neutral",
        corporate_insiders=corp_insiders or [],
        politician_trades=pol_trades or []
    )

    # Update Cache
    ticker_cache[symbol] = brief
    
    return brief

@router.get("/ticker/{symbol}/history", response_model=List[PricePoint])
async def get_ticker_history(symbol: str, period: str = "1mo"):
    """
    Get historical price data.
    """
    # Run in executor to avoid blocking
    data = await run_sync(get_price_history, symbol, period)
    return [PricePoint(**item) for item in data]

@router.get("/trending", response_model=List[str])
async def get_trending_tickers():
    """
    Get trending tickers.
    """
    import random
    # get_sp500_tickers performs a web scrape? Yes. Should be cached or async.
    # For now, let's run in executor.
    
    # Ideally detailed cache here too
    all_tickers = await run_sync(get_sp500_tickers)
    return random.sample(all_tickers, 10)
