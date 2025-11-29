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
    retail_sentiment: Optional[str] = None # 0.0 to 1.0 (Calculated based on sentiment balance/volatility)

class InsiderTransaction(BaseModel):
    holder: str
    shares: str
    position: str # "Direct" or "Indirect"
    date: str
    transaction_text: str = ""

class PoliticianTrade(BaseModel):
    politician: str
    party: str # "D" or "R"
    date: str
    type: str # "Purchase" or "Sale"
    amount: str
    ticker: str

class AnalyzedArticle(Article):
    sentiment: SentimentResult

class PricePoint(BaseModel):
    time: str
    price: float
    ma50: Optional[float] = None
    ma100: Optional[float] = None
    ema50: Optional[float] = None
    ema100: Optional[float] = None

class TickerBrief(BaseModel):
    symbol: str
    bullish_count: int
    bearish_count: int
    neutral_count: int
    articles: List[AnalyzedArticle]
    safety_score: float
    
    # New Metrics
    price: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    average_volume: Optional[int] = None
    exchange: Optional[str] = None
    put_call_ratio: Optional[float] = None
    institutional_holders: List[str] = []
    insider_sentiment: Optional[str] = None
    retail_sentiment: Optional[str] = None
    
    # Tracking
    corporate_insiders: List[InsiderTransaction] = []
    politician_trades: List[PoliticianTrade] = [] # 0.0 to 1.0 (Calculated based on sentiment balance/volatility)
