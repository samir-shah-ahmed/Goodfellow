from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TickerBrief, AnalyzedArticle, SentimentResult, PricePoint
from app.services.ingest import yfinance_scrape, get_sp500_tickers
from app.services.classifier import analyze_sentiment

router = APIRouter()

@router.get("/ticker/{symbol}", response_model=TickerBrief)
def get_ticker_brief(symbol: str):
    """
    Get a balanced brief for a specific ticker.
    """
    # 1. Scrape news
    articles_data = yfinance_scrape(tickers=[symbol], max_tickers=1)
    if not articles_data:
        raise HTTPException(status_code=404, detail=f"No news found for ticker {symbol}")

    # 2. Analyze sentiment
    analyzed_articles = []
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0

    for art in articles_data:
        text = art['headline']
        stance, confidence = analyze_sentiment(text)
        
        sentiment = SentimentResult(stance=stance, confidence=confidence)
        analyzed_article = AnalyzedArticle(
            headline=text,
            ticker=symbol,
            sentiment=sentiment,
            link=art.get('link') # Ingest might need update to return links for ticker scrape too
        )
        analyzed_articles.append(analyzed_article)

        if stance == 'positive':
            bullish_count += 1
        elif stance == 'negative':
            bearish_count += 1
        else:
            neutral_count += 1

    # 3. Calculate Safety Score (Simple Heuristic)
    total = bullish_count + bearish_count + neutral_count
    if total == 0:
        safety_score = 0.5
    else:
        # More bullish = higher score, more bearish = lower score.
        # Neutral pulls towards 0.5
        score = (bullish_count * 1.0 + neutral_count * 0.5 + bearish_count * 0.0) / total
        safety_score = round(score, 2)

    # 4. Fetch Advanced Metrics
    from app.services.ingest import get_ticker_info, get_options_data
    from app.services.sentiment_social import get_retail_sentiment
    from app.services.insider import get_corporate_insiders
    from app.services.politician import get_politician_trades
    
    ticker_info = get_ticker_info(symbol)
    put_call_ratio = get_options_data(symbol)
    retail_sent = get_retail_sentiment(symbol)
    
    # Fetch Tracking Data
    corp_insiders = get_corporate_insiders(symbol)
    pol_trades = get_politician_trades(symbol)

    return TickerBrief(
        symbol=symbol.upper(),
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
        retail_sentiment=retail_sent,
        corporate_insiders=corp_insiders,
        politician_trades=pol_trades
    )

@router.get("/ticker/{symbol}/history", response_model=List[PricePoint])
def get_ticker_history(symbol: str, period: str = "1mo"):
    """
    Get historical price data for a ticker.
    """
    from app.services.ingest import get_price_history
    from app.models.schemas import PricePoint
    
    data = get_price_history(symbol, period)
    return [PricePoint(**item) for item in data]

@router.get("/trending", response_model=List[str])
def get_trending_tickers():
    """
    Get a list of trending tickers.
    For MVP, this just returns a random subset of S&P 500.
    """
    import random
    all_tickers = get_sp500_tickers()
    return random.sample(all_tickers, 10)
