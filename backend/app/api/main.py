from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.core.schemas import IngestRequest
from app.services.ingest.newsapi_ingestor import ingest_newsapi
from app.services.ingest.rss_ingestor import ingest_rss

try:
    from app.core.logger import setup_logging, RequestIdMiddleware
    _HAS_LOGGING = True
except Exception:
    _HAS_LOGGING = False


def create_app() -> FastAPI:
    settings = get_settings()


    if _HAS_LOGGING:
        setup_logging()

    app = FastAPI(title="Balanced Alpha Ingestion")

    
    origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if _HAS_LOGGING:
        app.add_middleware(RequestIdMiddleware)

    
    @app.get("/health")
    def health(request: Request):
        return {"ok": True}

    @app.post("/ingest/newsapi")
    def run_newsapi(req: IngestRequest, request: Request):
        return ingest_newsapi(req.tickers, req.limit_per_ticker)

    @app.post("/ingest/rss")
    def run_rss(req: IngestRequest, request: Request):
        return ingest_rss(req.tickers, req.limit_per_ticker)
    
    

    return app



app = create_app()
