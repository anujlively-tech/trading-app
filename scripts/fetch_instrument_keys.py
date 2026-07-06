"""
One-time helper: downloads Upstox's NSE instrument master and prints the
instrument_key for each stock in your watchlist, so you can paste them into
app/config.py.

Run:  python scripts/fetch_instrument_keys.py
"""
import gzip
import json
import httpx
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.config import WATCHLIST

URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"


def main():
    print("Downloading Upstox NSE instrument master...")
    resp = httpx.get(URL, timeout=60, follow_redirects=True)
    data = json.loads(gzip.decompress(resp.content))

    by_symbol = {row["trading_symbol"]: row for row in data if row.get("instrument_type") == "EQ"}

    print("\nMatches for your watchlist:\n")
    for stock in WATCHLIST:
        row = by_symbol.get(stock.symbol)
        if row:
            print(f'Stock("{stock.name}", "{stock.symbol}", "{row["instrument_key"]}"),')
        else:
            print(f'# NOT FOUND: {stock.name} ({stock.symbol}) — check exact trading symbol on NSE')


if __name__ == "__main__":
    main()
