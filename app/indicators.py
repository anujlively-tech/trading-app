"""
Streaming technical indicators, computed incrementally as new ticks/candles arrive.
Each symbol gets its own IndicatorState so indicators update in O(1) per tick
rather than recomputing over the whole day's data.
"""
from collections import deque
from dataclasses import dataclass, field


@dataclass
class IndicatorState:
    symbol: str
    # VWAP accumulators (reset at market open, 09:15 IST)
    cum_price_volume: float = 0.0
    cum_volume: float = 0.0
    vwap: float = 0.0

    # Rolling closes for RSI / EMA / MACD
    closes: deque = field(default_factory=lambda: deque(maxlen=250))
    ema_values: dict = field(default_factory=dict)     # period -> current EMA
    macd_line: float = 0.0
    macd_signal: float = 0.0
    macd_hist: float = 0.0
    rsi: float = 50.0
    avg_gain: float = 0.0
    avg_loss: float = 0.0

    # 1-min volume tracking
    minute_volumes: deque = field(default_factory=lambda: deque(maxlen=390))  # full trading day
    last_cum_volume_snapshot: float = 0.0


def update_vwap(state: IndicatorState, price: float, volume: float) -> float:
    """VWAP = cumulative(price * volume) / cumulative(volume), reset daily."""
    state.cum_price_volume += price * volume
    state.cum_volume += volume
    if state.cum_volume > 0:
        state.vwap = state.cum_price_volume / state.cum_volume
    return state.vwap


def update_ema(state: IndicatorState, price: float, period: int) -> float:
    k = 2 / (period + 1)
    prev = state.ema_values.get(period)
    ema = price if prev is None else (price - prev) * k + prev
    state.ema_values[period] = ema
    return ema


def update_macd(state: IndicatorState, price: float, fast=12, slow=26, signal=9) -> tuple[float, float, float]:
    ema_fast = update_ema(state, price, fast)
    ema_slow = update_ema(state, price, slow)
    macd = ema_fast - ema_slow
    # signal line = EMA of macd values
    k = 2 / (signal + 1)
    prev_signal = state.macd_signal or macd
    signal_line = (macd - prev_signal) * k + prev_signal
    state.macd_line = macd
    state.macd_signal = signal_line
    state.macd_hist = macd - signal_line
    return macd, signal_line, state.macd_hist


def update_rsi(state: IndicatorState, price: float, period: int = 14) -> float:
    state.closes.append(price)
    if len(state.closes) < 2:
        return state.rsi
    change = state.closes[-1] - state.closes[-2]
    gain = max(change, 0)
    loss = max(-change, 0)
    if len(state.closes) <= period:
        # simple average while warming up
        state.avg_gain = (state.avg_gain * (len(state.closes) - 2) + gain) / (len(state.closes) - 1)
        state.avg_loss = (state.avg_loss * (len(state.closes) - 2) + loss) / (len(state.closes) - 1)
    else:
        state.avg_gain = (state.avg_gain * (period - 1) + gain) / period
        state.avg_loss = (state.avg_loss * (period - 1) + loss) / period
    if state.avg_loss == 0:
        state.rsi = 100.0
    else:
        rs = state.avg_gain / state.avg_loss
        state.rsi = 100 - (100 / (1 + rs))
    return state.rsi


def record_minute_volume(state: IndicatorState, cumulative_volume: float) -> float:
    """Upstox gives cumulative day volume in ticks; derive per-minute delta."""
    delta = max(cumulative_volume - state.last_cum_volume_snapshot, 0)
    state.last_cum_volume_snapshot = cumulative_volume
    state.minute_volumes.append(delta)
    return delta


def process_tick(state: IndicatorState, ltp: float, cumulative_volume: float, last_traded_qty: float = 0.0) -> dict:
    """Call this on every tick to refresh all indicators for one symbol."""
    from . import config
    update_vwap(state, ltp, last_traded_qty)
    update_rsi(state, ltp, config.RSI_PERIOD)
    for p in config.EMA_PERIODS:
        update_ema(state, ltp, p)
    update_macd(state, ltp, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL)
    minute_vol = record_minute_volume(state, cumulative_volume)

    return {
        "symbol": state.symbol,
        "ltp": ltp,
        "vwap": round(state.vwap, 2),
        "rsi": round(state.rsi, 2),
        "ema": {p: round(v, 2) for p, v in state.ema_values.items()},
        "macd": round(state.macd_line, 3),
        "macd_signal": round(state.macd_signal, 3),
        "macd_hist": round(state.macd_hist, 3),
        "minute_volume": minute_vol,
        "cum_volume": cumulative_volume,
        "above_vwap": ltp > state.vwap if state.vwap else None,
    }
