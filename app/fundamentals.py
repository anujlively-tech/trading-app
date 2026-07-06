"""
Fundamentals — NSE's public quote API returns basic fundamentals (P/E, market
cap, 52-week range, delivery %). For deeper fundamentals (ROE, debt/equity,
quarterly results history), integrate a paid source (Screener.in has no public
API but permits scraping their site for personal use per their terms; or use
a paid data vendor like Tijori Finance / Trendlyne API).
"""
import httpx

NSE_QUOTE_URL = "https://www.nseindia.com/api/quote-equity?symbol={symbol}"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}


async def get_basic_fundamentals(symbol: str) -> dict:
    """NSE requires a session cookie from visiting the homepage first."""
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10) as client:
        await client.get("https://www.nseindia.com")  # sets cookies
        resp = await client.get(NSE_QUOTE_URL.format(symbol=symbol))
        resp.raise_for_status()
        data = resp.json()
        price_info = data.get("priceInfo", {})
        metadata = data.get("metadata", {})
        return {
            "symbol": symbol,
            "last_price": price_info.get("lastPrice"),
            "52w_high": price_info.get("weekHighLow", {}).get("max"),
            "52w_low": price_info.get("weekHighLow", {}).get("min"),
            "pe_ratio": data.get("metadata", {}).get("pdSymbolPe"),
            "industry": metadata.get("industry"),
            "market_cap": data.get("securityInfo", {}).get("issuedSize"),
        }
