import feedparser, httpx, hashlib, datetime as dt
from app.services.ingest.cleaner import clean_html
from app.services.ingest.linker import link_tickers
from app.core.db import SessionLocal, engine
from app.core.logger import logger
from app.models.document import Document
from app.models.doc_ticker import DocTicker
from app.models.base import Base
from sqlalchemy import select

RSS_FEEDS = [
    "https://www.marketwatch.com/rss/topstories",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=news",
]

def sha256(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def ensure_tables():
    Base.metadata.create_all(bind=SessionLocal.kw["bind"])  # type: ignore

def fetch_page(url: str) -> str:
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(url, follow_redirects=True)
            r.raise_for_status()
            return r.text
    except Exception as e:
        logger.warning(f"fetch fail {url}: {e}")
        return ""

def ingest_rss(tickers: list[str], limit: int = 50) -> dict:
    ensure_tables()
    inserted, skipped = 0, 0
    with SessionLocal() as db:
        for feed in RSS_FEEDS:
            d = feedparser.parse(feed)
            for entry in d.entries[:limit]:
                url = entry.get("link")
                if not url:
                    continue
                # De-dup URL
                already = db.execute(select(Document).where(Document.url == url)).scalar_one_or_none()
                if already:
                    skipped += 1
                    continue
                title = entry.get("title", "")
                html = fetch_page(url)
                text = clean_html(html or title)
                if not text:
                    continue
                source = d.feed.get("title", "rss")
                published = entry.get("published") or entry.get("updated")
                try:
                    published_dt = dt.datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else None
                except Exception:
                    published_dt = None
                h = sha256((title + source + (published or "")).strip())

                doc = Document(
                    url=url,
                    source=source[:255],
                    title=title[:1024],
                    author=None,
                    published_at=published_dt,
                    clean_text=text,
                    text_hash=h
                )
                db.add(doc)
                db.flush()

                links = link_tickers(title, text, tickers)
                for tk, rel in links:
                    db.add(DocTicker(doc_id=doc.id, ticker=tk, relevance=rel))
                inserted += 1
        db.commit()
    return {"inserted": inserted, "skipped": skipped}