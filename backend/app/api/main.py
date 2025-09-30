from fastapi import FastAPI
from app.core.schemas import IngestRequest
from app.services.ingest.newsapi_ingestor import ingest_newsapi
from app.services.ingest.rss_ingestor import ingest_rss

app = FastAPI(title="Balanced Alpha Ingestion")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ingest/newsapi")
def run_newsapi(req: IngestRequest):
    return ingest_newsapi(req.tickers, req.limit_per_ticker)

@app.post("/ingest/rss")
def run_rss(req: IngestRequest):
    return ingest_rss(req.tickers, req.limit_per_ticker)