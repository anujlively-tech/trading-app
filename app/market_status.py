"""
Global + India market index snapshots. Uses Yahoo Finance's free quote
endpoint (unofficial, no key required) since Upstox only covers NSE/BSE
instruments and won't give you S&P 500 / Nikkei / etc.
"""
import httpx
from . import config

YF_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"


async def _fetch_quotes(symbols: list[str]) -> dict:
    joined = ",".join(symbols)
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "Mozilla/5.0"}) as client:
        resp = await client.get(YF_QUOTE_URL.format(symbols=joined))
        resp.raise_for_status()
        results = resp.json().get("quoteResponse", {}).get("result", [])
        return {
            q["symbol"]: {
                "price": q.get("regularMarketPrice"),
                "change": q.get("regularMarketChange"),
                "change_pct": q.get("regularMarketChangePercent"),
                "market_state": q.get("marketState"),
            }
            for q in results
        }


async def get_global_market_status() -> dict:
    symbol_map = config.GLOBAL_INDICES
    quotes = await _fetch_quotes(list(symbol_map.values()))
    return {name: quotes.get(sym, {}) for name, sym in symbol_map.items()}


async def get_india_market_status() -> dict:
    symbol_map = config.INDIA_INDICES
    quotes = await _fetch_quotes(list(symbol_map.values()))
    return {name: quotes.get(sym, {}) for name, sym in symbol_map.items()}
