"""
News aggregation via RSS (free, no API key needed). For company-specific news,
we filter general market feeds by company name/symbol — for deeper coverage,
plug in a paid news API (e.g. NewsAPI.org, Finnhub) by adding a fetch function
here with the same return shape.
"""
import feedparser
import httpx
from datetime import datetime, timezone

FEEDS = {
    "india_market": [
        "https://www.moneycontrol.com/rss/marketreports.xml",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    ],
    "global_market": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ],
    "corporate_filings": [
        # NSE corporate announcements (public feed)
        "https://nsearchives.nseindia.com/content/RSS/Corporate_Announcements.xml",
    ],
}


async def _fetch_feed(url: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        parsed = feedparser.parse(resp.text)
        return [
            {
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published": e.get("published", ""),
                "summary": e.get("summary", "")[:300],
            }
            for e in parsed.entries[:20]
        ]


async def get_market_news(category: str) -> list[dict]:
    urls = FEEDS.get(category, [])
    all_items = []
    for url in urls:
        try:
            all_items.extend(await _fetch_feed(url))
        except Exception as e:
            all_items.append({"title": f"[feed error: {url}]", "summary": str(e), "link": "", "published": ""})
    return all_items


async def get_company_news(company_name: str, symbol: str) -> list[dict]:
    """Filters India-market + corporate-filing feeds for mentions of this company."""
    india_items = await get_market_news("india_market")
    filings = await get_market_news("corporate_filings")
    keywords = [company_name.lower(), symbol.lower()]
    matches = [
        item for item in (india_items + filings)
        if any(kw in (item["title"] + item["summary"]).lower() for kw in keywords)
    ]
    return matches


async def get_all_news_bundle() -> dict:
    return {
        "india_market": await get_market_news("india_market"),
        "global_market": await get_market_news("global_market"),
        "corporate_filings": await get_market_news("corporate_filings"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
