"""
Compiles the daily report: ranked table + technical picture + news highlights
for each of the 30 stocks, plus a market overview section.
"""
from datetime import datetime
from . import market_status, news, ranking


async def build_daily_report(indicator_snapshots: dict, minute_volume_history: dict) -> dict:
    """
    indicator_snapshots: {symbol: {ltp, ema, rsi, macd_hist, vwap}}
    minute_volume_history: {symbol: [minute volumes today]}
    """
    results = []
    for symbol, snap in indicator_snapshots.items():
        r = ranking.score_stock(
            symbol=symbol,
            ltp=snap["ltp"],
            ema=snap["ema"],
            rsi=snap["rsi"],
            macd_hist=snap["macd_hist"],
            vwap=snap["vwap"],
            minute_volumes=minute_volume_history.get(symbol, []),
        )
        results.append(r)

    ranked = ranking.rank_all(results)

    global_status = await market_status.get_global_market_status()
    india_status = await market_status.get_india_market_status()
    news_bundle = await news.get_all_news_bundle()

    return {
        "generated_at": datetime.now().isoformat(),
        "global_markets": global_status,
        "india_markets": india_status,
        "rankings": [
            {
                "rank": r.rank,
                "symbol": r.symbol,
                "score": r.score,
                "breakdown": r.breakdown,
                "technical_picture": _describe_technical_picture(r),
            }
            for r in ranked
        ],
        "news": news_bundle,
    }


def _describe_technical_picture(r: ranking.RankResult) -> str:
    b = r.breakdown
    parts = []
    parts.append("uptrend" if b["trend"] > 0.3 else "downtrend" if b["trend"] < -0.3 else "sideways")
    parts.append("bullish momentum" if b["momentum"] > 0.3 else "bearish momentum" if b["momentum"] < -0.3 else "neutral momentum")
    parts.append("above VWAP" if b["vwap"] > 0 else "below VWAP")
    parts.append("volume picking up" if b["volume"] > 0.2 else "volume subdued" if b["volume"] < -0.2 else "normal volume")
    return ", ".join(parts)
