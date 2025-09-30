from pydantic import BaseModel

class IngestRequest(BaseModel):
    tickers: list[str] = ["AAPL", "MSFT", "NVDA"]
    limit_per_ticker: int = 10