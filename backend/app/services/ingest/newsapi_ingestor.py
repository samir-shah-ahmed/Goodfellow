import httpx, hashlib, datetime as dt
from app.services.ingest.cleaner import clean_html
from app.services.ingest.linker import link_tickers
from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.core.logger import logger
from app.models.document import Document
from app.models.doc_ticker import DocTicker
from app.models.base import Base
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

NEWSAPI_URL = "https://newsapi.org/v2/everything"

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def ensure_tables():
    Base.metadata.create_all(bind=SessionLocal.kw["bind"])  # type: ignore

def fetch_newsapi(query: str, page_size: int = 20):
    if not settings.NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not set; skip NewsAPI.")
        return []
    params = {
        "q": query,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": settings.NEWSAPI_KEY,
    }
    with httpx.Client(timeout=20) as client:
        r = client.get(NEWSAPI_URL, params=params)
        r.raise_for_status()
        return r.json().get("articles", [])

def ingest_newsapi(tickers: list[str], limit_per_ticker: int = 10) -> dict:
    ensure_tables()
    inserted, skipped = 0, 0
    with SessionLocal() as db:
        for t in tickers:
            # Basic query: ticker OR company name alias
            q = f'"{t}" OR { " OR ".join([a for a in ([])]) }'
            articles = fetch_newsapi(q, page_size=limit_per_ticker)
            for a in articles:
                url = a.get("url")
                if not url:
                    continue
                html = a.get("content") or a.get("description") or ""
                title = a.get("title") or ""
                source = (a.get("source") or {}).get("name") or "unknown"
                author = a.get("author")
                published_at = a.get("publishedAt")
                try:
                    published_dt = dt.datetime.fromisoformat(published_at.replace("Z","+00:00")) if published_at else None
                except Exception:
                    published_dt = None

                # Clean & hash
                text = clean_html(html or title)
                if not text:
                    continue
                h = sha256((title + source + (published_at or "")).strip())

                # De-dup by URL or hash
                already = db.execute(select(Document).where(Document.url == url)).scalar_one_or_none()
                if already:
                    skipped += 1
                    continue

                doc = Document(
                    url=url,
                    source=source,
                    title=title[:1024],
                    author=author[:255] if author else None,
                    published_at=published_dt,
                    clean_text=text,
                    text_hash=h
                )
                db.add(doc)
                try:
                    db.flush()  # get doc.id
                except IntegrityError:
                    db.rollback()
                    skipped += 1
                    continue

                # Link tickers (simple)
                links = link_tickers(title, text, [t])
                for tk, rel in links:
                    db.add(DocTicker(doc_id=doc.id, ticker=tk, relevance=rel))

                inserted += 1
        db.commit()
    return {"inserted": inserted, "skipped": skipped}