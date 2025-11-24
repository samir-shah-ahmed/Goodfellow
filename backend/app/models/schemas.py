from pydantic import BaseModel
from typing import List, Optional

class Article(BaseModel):
    headline: str
    source: Optional[str] = None
    link: Optional[str] = None
    ticker: Optional[str] = None
    published_at: Optional[str] = None

class SentimentResult(BaseModel):
    stance: str
    confidence: float

class AnalyzedArticle(Article):
    sentiment: SentimentResult

class TickerBrief(BaseModel):
    symbol: str
    bullish_count: int
    bearish_count: int
    neutral_count: int
    articles: List[AnalyzedArticle]
    safety_score: float # 0.0 to 1.0 (Calculated based on sentiment balance/volatility)
