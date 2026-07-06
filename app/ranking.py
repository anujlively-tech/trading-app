"""
Ranking engine — combines technical signals into a single composite score
per stock so the 30-name watchlist can be ranked for the daily report.

This is a transparent, editable rules-based scorer (not a black box) so you
can see exactly why a stock ranked where it did, and adjust weights easily.
"""
from dataclasses import dataclass


WEIGHTS = {
    "trend": 0.30,      # price vs EMA stack (9/21/50) — trend alignment
    "momentum": 0.25,   # RSI positioning
    "macd": 0.20,       # MACD histogram direction/strength
    "vwap": 0.15,       # price vs VWAP (intraday strength)
    "volume": 0.10,     # relative volume vs recent average
}


@dataclass
class RankResult:
    symbol: str
    score: float
    breakdown: dict
    rank: int = 0


def _trend_score(ema: dict, ltp: float) -> float:
    """+1 if price above all EMAs in rising order (9>21>50), -1 if fully inverted."""
    e9, e21, e50 = ema.get(9), ema.get(21), ema.get(50)
    if not all([e9, e21, e50]):
        return 0.0
    if ltp > e9 > e21 > e50:
        return 1.0
    if ltp < e9 < e21 < e50:
        return -1.0
    # partial alignment
    above_count = sum([ltp > e9, ltp > e21, ltp > e50])
    return (above_count - 1.5) / 1.5  # scales roughly -1..+1


def _momentum_score(rsi: float) -> float:
    if rsi >= 70:
        return 0.6           # strong but watch for overbought
    if rsi >= 55:
        return 1.0           # healthy bullish momentum
    if rsi <= 30:
        return -0.6
    if rsi <= 45:
        return -1.0
    return 0.0                # neutral zone 45-55


def _macd_score(macd_hist: float, price_scale: float) -> float:
    if price_scale <= 0:
        return 0.0
    normalized = macd_hist / price_scale * 100  # normalize by price level
    return max(-1.0, min(1.0, normalized * 5))


def _vwap_score(ltp: float, vwap: float) -> float:
    if not vwap:
        return 0.0
    pct = (ltp - vwap) / vwap * 100
    return max(-1.0, min(1.0, pct * 2))


def _volume_score(minute_volumes: list) -> float:
    if len(minute_volumes) < 5:
        return 0.0
    recent = minute_volumes[-1]
    avg = sum(minute_volumes[:-1]) / max(len(minute_volumes) - 1, 1)
    if avg == 0:
        return 0.0
    ratio = recent / avg
    return max(-1.0, min(1.0, (ratio - 1)))


def score_stock(symbol: str, ltp: float, ema: dict, rsi: float, macd_hist: float,
                 vwap: float, minute_volumes: list) -> RankResult:
    trend = _trend_score(ema, ltp)
    momentum = _momentum_score(rsi)
    macd = _macd_score(macd_hist, ltp)
    vwap_s = _vwap_score(ltp, vwap)
    volume = _volume_score(minute_volumes)

    breakdown = {"trend": trend, "momentum": momentum, "macd": macd, "vwap": vwap_s, "volume": volume}
    total = sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS)
    return RankResult(symbol=symbol, score=round(total, 3), breakdown=breakdown)


def rank_all(results: list[RankResult]) -> list[RankResult]:
    ordered = sorted(results, key=lambda r: r.score, reverse=True)
    for i, r in enumerate(ordered, start=1):
        r.rank = i
    return ordered
