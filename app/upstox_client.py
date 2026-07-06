"""
Upstox integration: OAuth login, historical data, and the live market-data
WebSocket feed (LTP, full quote with market depth / order book, and OHLC).

Docs: https://upstox.com/developer/api-documentation/
"""
import asyncio
import json
import ssl
import httpx
import websockets
from google.protobuf.json_format import MessageToDict

from . import config

HISTORICAL_URL = "https://api.upstox.com/v2/historical-candle"
WS_AUTH_URL = "https://api.upstox.com/v2/feed/market-data-feed/authorize"

# No login flow needed — we use the long-lived Analytics Token (config.UPSTOX_ACCESS_TOKEN)
# directly on every request. It's read-only (market data only) and valid ~1 year.


async def get_historical_candles(instrument_key: str, interval: str, from_date: str, to_date: str) -> dict:
    """interval: '1minute', '30minute', 'day', 'week', 'month'"""
    url = f"{HISTORICAL_URL}/{instrument_key}/{interval}/{to_date}/{from_date}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"Accept": "application/json"})
        resp.raise_for_status()
        return resp.json()


async def get_intraday_candles(instrument_key: str, interval: str = "1minute") -> dict:
    """Today's intraday candles (minute-by-minute OHLCV) — used for volume + VWAP."""
    url = f"https://api.upstox.com/v2/historical-candle/intraday/{instrument_key}/{interval}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {config.UPSTOX_ACCESS_TOKEN}",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def _get_ws_url() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            WS_AUTH_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {config.UPSTOX_ACCESS_TOKEN}",
            },
        )
        resp.raise_for_status()
        return resp.json()["data"]["authorized_redirect_uri"]


class UpstoxFeed:
    """
    Live market-data WebSocket. Streams LTP, full market depth (order book,
    top 5 bid/ask), and OHLC ticks for subscribed instruments.
    Feed messages are Protobuf-encoded; requires Upstox's compiled proto
    (MarketDataFeed.proto) — see Upstox docs for the schema file to compile
    with `protoc` into market_data_feed_pb2.py, imported below.
    """
    def __init__(self, on_tick):
        self.on_tick = on_tick  # callback(instrument_key: str, tick: dict)
        self._ws = None
        self._running = False

    async def connect_and_subscribe(self, instrument_keys: list[str]):
        ws_url = await _get_ws_url()
        ssl_ctx = ssl.create_default_context()
        async with websockets.connect(ws_url, ssl=ssl_ctx) as ws:
            self._ws = ws
            self._running = True
            sub_msg = {
                "guid": "trading-dashboard",
                "method": "sub",
                "data": {"mode": "full", "instrumentKeys": instrument_keys},
            }
            await ws.send(json.dumps(sub_msg).encode("utf-8"))
            while self._running:
                raw = await ws.recv()
                tick = self._decode(raw)
                if tick:
                    for key, payload in tick.get("feeds", {}).items():
                        await self.on_tick(key, payload)

    def _decode(self, raw_bytes) -> dict:
        # Requires market_data_feed_pb2 generated from Upstox's proto schema.
        try:
            from . import market_data_feed_pb2 as pb
            feed = pb.FeedResponse()
            feed.ParseFromString(raw_bytes)
            return MessageToDict(feed)
        except ImportError:
            # Fallback: log raw bytes until the proto module is compiled (see README).
            return {}

    async def close(self):
        self._running = False
        if self._ws:
            await self._ws.close()
