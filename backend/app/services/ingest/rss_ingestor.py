from __future__ import annotations
from typing import List, Dict, Any, Optional
import httpx
import datetime as dt
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from app.core.settings import get_settings
from app.core.logger import get_logger

log = get_logger("ingest.rss")
settings = get_settings()

# Minimal starter feed list (general finance). Replace/extend from DB later.
DEFAULT_RSS_FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",      # WSJ Markets
    "https://www.marketwatch.com/rss/topstories",          # MarketWatch
    "https://finance.yahoo.com/news/rssindex",            # Yahoo Finance
    "https://www.investing.com/rss/news_25.rss",          # Investing.com
]

def _excerpt_if_needed(text: Optional[str], domain: Optional[str]) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    d = (domain or "").lower()
    if (not settings.FEATURE_STORE_FULLTEXT) or (d in settings.excerpt_domains_set):
        return t[: settings.EXCERPT_MAX_CHARS]
    return t

def _parse_rss(xml_text: str) -> List[Dict[str, Any]]:
    """
    Parse a simple RSS/Atom feed to a list of items with title/link/summary/pubdate.
    Handles common RSS (channel/item) and Atom (feed/entry) shapes.
    """
    items: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    # RSS (channel/item)
    channel = root.find("channel")
    if channel is not None:
        for it in channel.findall("item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            desc = (it.findtext("description") or "").strip()
            pubdate = (it.findtext("pubDate") or "").strip()
            items.append({"title": title, "link": link, "summary": desc, "published_at": pubdate})
        return items

    # Atom (feed/entry)
    for it in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = (it.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = it.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href").strip() if link_el is not None and link_el.get("href") else ""
        summary = (it.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
        updated = (it.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        items.append({"title": title, "link": link, "summary": summary, "published_at": updated})
    return items

def _matches_any_ticker(text: str, tickers: List[str]) -> Optional[str]:
    """Return the first ticker symbol that appears in text (case-insensitive), else None."""
    if not text:
        return None
    low = text.lower()
    for t in tickers or []:
        if (t or "").lower() in low:
            return t
    return None

def ingest_rss(tickers: List[str], limit_per_ticker: int) -> Dict[str, Any]:
    """
    Pull a set of public RSS feeds, filter by ticker mentions in title/summary,
    and return normalized items. Later, move feed list to DB and do smarter matching.
    """
    headers = {"User-Agent": settings.USER_AGENT}
    timeout = httpx.Timeout(settings.FETCH_TIMEOUT_SECS)
    per_symbol_limit = max(1, int(limit_per_ticker or settings.DEFAULT_PAGE_SIZE))

    # Basic per-symbol buckets
    buckets: Dict[str, List[Dict[str, Any]]] = {t: [] for t in (tickers or [])}

    feeds = DEFAULT_RSS_FEEDS  # TODO: load from DB/config in Phase 3
    with httpx.Client(timeout=timeout, headers=headers) as client:
        for feed_url in feeds:
            try:
                resp = client.get(feed_url)
                resp.raise_for_status()
                parsed = _parse_rss(resp.text)
            except httpx.HTTPError as e:
                log.error(f"RSS fetch failed: {feed_url} | {e}")
                continue

            for raw in parsed:
                title = raw.get("title", "")
                summary = raw.get("summary", "")
                link = raw.get("link", "")
                matched = _matches_any_ticker(title + " " + summary, tickers)
                if not matched:
                    continue  # skip items that don't mention a ticker

                domain = urlparse(link).netloc
                norm = {
                    "ticker": matched,
                    "source_domain": domain,
                    "title": title,
                    "url": link,
                    "published_at": raw.get("published_at"),
                    "summary": _excerpt_if_needed(summary, domain),
                }

                # enforce per-symbol limit
                if len(buckets[matched]) < per_symbol_limit:
                    buckets[matched].append(norm)

    # Flatten
    items: List[Dict[str, Any]] = []
    for t in tickers or []:
        items.extend(buckets.get(t, []))

    log.info(f"rss collected total={len(items)} across tickers={tickers}")
    return {"provider": "rss", "items": items, "count": len(items)}