"""
FastAPI app — entry point.

Run with:  uvicorn app.main:app --reload --port 8000

Endpoints:
  GET  /api/watchlist           -> the 30 configured stocks
  GET  /api/news/{category}     -> india_market | global_market | corporate_filings
  GET  /api/news/company/{symbol}
  GET  /api/fundamentals/{symbol}
  GET  /api/markets/global
  GET  /api/markets/india
  GET  /api/report              -> full ranked daily report
  WS   /ws/live                 -> streams live ticks + indicators for the watchlist
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from . import config, upstox_client, indicators, news, fundamentals, market_status, report

app = FastAPI(title="Trading Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict this to your actual frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory state: one IndicatorState per symbol
indicator_states = {s.symbol: indicators.IndicatorState(symbol=s.symbol) for s in config.WATCHLIST}
latest_snapshots: dict = {}
connected_clients: list[WebSocket] = []


@app.get("/api/watchlist")
def get_watchlist():
    return [{"name": s.name, "symbol": s.symbol} for s in config.WATCHLIST]


@app.get("/api/news/{category}")
async def get_news(category: str):
    return await news.get_market_news(category)


@app.get("/api/news/company/{symbol}")
async def get_company_news(symbol: str):
    stock = next((s for s in config.WATCHLIST if s.symbol == symbol), None)
    if not stock:
        return {"error": "symbol not in watchlist"}
    return await news.get_company_news(stock.name, stock.symbol)


@app.get("/api/fundamentals/{symbol}")
async def get_fundamentals(symbol: str):
    return await fundamentals.get_basic_fundamentals(symbol)


@app.get("/api/markets/global")
async def get_global_markets():
    return await market_status.get_global_market_status()


@app.get("/api/markets/india")
async def get_india_markets():
    return await market_status.get_india_market_status()


@app.get("/api/report")
async def get_report():
    minute_vol_history = {sym: list(st.minute_volumes) for sym, st in indicator_states.items()}
    return await report.build_daily_report(latest_snapshots, minute_vol_history)


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive / ignore client pings
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def _broadcast(payload: dict):
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for d in dead:
        connected_clients.remove(d)


async def _on_tick(instrument_key: str, feed_payload: dict):
    """Callback wired to the Upstox feed — updates indicators and broadcasts to clients."""
    stock = next((s for s in config.WATCHLIST if s.instrument_key == instrument_key), None)
    if not stock:
        return
    ltp_data = feed_payload.get("ff", {}).get("marketFF", {}) or feed_payload.get("ltpc", {})
    ltp = ltp_data.get("ltp") or ltp_data.get("lastPrice")
    cum_volume = ltp_data.get("vtt", 0)  # volume traded today
    if ltp is None:
        return
    state = indicator_states[stock.symbol]
    snapshot = indicators.process_tick(state, float(ltp), float(cum_volume))
    latest_snapshots[stock.symbol] = snapshot
    # order book / market depth, if present in the full feed
    depth = feed_payload.get("marketFF", {}).get("marketLevel", {}).get("bidAskQuote")
    if depth:
        snapshot["order_book"] = depth
    await _broadcast(snapshot)


@app.on_event("startup")
async def start_feed():
    """Launches the Upstox WebSocket feed as a background task on server start."""
    instrument_keys = [s.instrument_key for s in config.WATCHLIST if s.instrument_key]
    if not instrument_keys or not config.UPSTOX_ACCESS_TOKEN:
        print("⚠ No instrument keys or access token set — live feed not started. "
              "Fill in config.py's WATCHLIST instrument_keys, and set the "
              "UPSTOX_ACCESS_TOKEN environment variable to your Analytics Token, then restart.")
        return
    feed = upstox_client.UpstoxFeed(on_tick=_on_tick)
    asyncio.create_task(feed.connect_and_subscribe(instrument_keys))
