from __future__ import annotations
from typing import List, Dict, Any, Optional
import httpx
from urllib.parse import urlparse

from app.core.settings import get_settings
from app.core.logger import get_logger

log = get_logger("ingest.newsapi")
settings = get_settings()

def _excerpt_if_needed(text: Optional[str], domain: Optional[str]) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    d = (domain or "").lower()
    if (not settings.FEATURE_STORE_FULLTEXT) or (d in settings.excerpt_domains_set):
        return t[: settings.EXCERPT_MAX_CHARS]
    return t

def ingest_newsapi(tickers: List[str], limit_per_ticker: int) -> Dict[str, Any]:
    """
    Query NewsAPI for each ticker keyword and return normalized items.
    Does NOT persist; returns data for the caller to store.
    """
    if not settings.NEWSAPI_KEY:
        log.warning("NEWSAPI_KEY not set — skipping NewsAPI ingest")
        return {"provider": "newsapi", "items": [], "count": 0, "skipped": True}

    headers = {"User-Agent": settings.USER_AGENT}
    timeout = httpx.Timeout(settings.FETCH_TIMEOUT_SECS)
    base_url = "https://newsapi.org/v2/everything"

    all_items: List[Dict[str, Any]] = []

    with httpx.Client(timeout=timeout, headers=headers) as client:
        for symbol in (tickers or []):
            params = {
                "q": symbol,
                "pageSize": max(1, int(limit_per_ticker or settings.DEFAULT_PAGE_SIZE)),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": settings.NEWSAPI_KEY,
            }
            try:
                resp = client.get(base_url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                log.error(f"NewsAPI request failed for {symbol}: {e}")
                continue

            articles = data.get("articles") or []
            for a in articles:
                url = a.get("url") or ""
                domain = urlparse(url).netloc
                item = {
                    "ticker": symbol,
                    "source_domain": domain,
                    "source_name": (a.get("source") or {}).get("name"),
                    "title": a.get("title"),
                    "url": url,
                    "published_at": a.get("publishedAt"),
                    "summary": _excerpt_if_needed(a.get("description") or a.get("content"), domain),
                    # raw text may be restricted by NewsAPI terms; keep minimal fields unless you fetch page content yourself
                }
                all_items.append(item)

            log.info(f"newsapi fetched={len(articles)} for {symbol}")

    return {"provider": "newsapi", "items": all_items, "count": len(all_items)}
