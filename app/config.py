"""
Central configuration: watchlist, API credentials, and constants.
Fill in UPSTOX_INSTRUMENT_KEY for each stock — these come from Upstox's
instrument master file (downloadable from https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz).
Match by 'name' or 'tradingsymbol' to get the instrument_key (format: NSE_EQ|ISIN).
"""
import os
from dataclasses import dataclass

# ---- Upstox credentials ----
# Using the long-lived "Analytics Token" (valid ~1 year, read-only market data).
# Set this as an environment variable — never hardcode it directly in this file.
UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "")

@dataclass
class Stock:
    name: str
    symbol: str            # NSE trading symbol
    instrument_key: str    # Upstox instrument key, e.g. "NSE_EQ|INE018A01030"
    sector: str = ""

# Fill instrument_key values by downloading Upstox's instrument master
# (one-time script provided in scripts/fetch_instrument_keys.py)
WATCHLIST = [
    Stock("Larsen & Toubro", "LT", ""),
    Stock("ICICI Bank", "ICICIBANK", ""),
    Stock("Bharat Electronics", "BEL", ""),
    Stock("KPIT Technologies", "KPITTECH", ""),
    Stock("Persistent Systems", "PERSISTENT", ""),
    Stock("Solar Industries", "SOLARINDS", ""),
    Stock("Polycab India", "POLYCAB", ""),
    Stock("Apollo Hospitals", "APOLLOHOSP", ""),
    Stock("Info Edge", "NAUKRI", ""),
    Stock("Poly Medicure", "POLYMED", ""),
    Stock("ABB India", "ABB", ""),
    Stock("Bharat Forge", "BHARATFORG", ""),
    Stock("Trent", "TRENT", ""),
    Stock("Titan Company", "TITAN", ""),
    Stock("Kaynes Technology", "KAYNES", ""),
    Stock("Dixon Technologies", "DIXON", ""),
    Stock("Hitachi Energy India", "POWERINDIA", ""),
    Stock("PB Fintech", "POLICYBZR", ""),
    Stock("CDSL", "CDSL", ""),
    Stock("HBL Engineering", "HBLENGINE", ""),
    Stock("Azad Engineering", "AZAD", ""),
    Stock("Data Patterns", "DATAPATTNS", ""),
    Stock("Zen Technologies", "ZENTEC", ""),
    Stock("MTAR Technologies", "MTARTECH", ""),
    Stock("Jyoti CNC Automation", "JYOTICNC", ""),
    Stock("Clean Science & Technology", "CLEAN", ""),
    Stock("DOMS Industries", "DOMS", ""),
    Stock("Elecon Engineering", "ELECON", ""),
    Stock("Black Box", "BBOX", ""),
    Stock("Aether Industries", "AETHER", ""),
]

# Global indices to track (via a free source like Yahoo Finance / Stooq since
# Upstox only covers Indian exchanges)
GLOBAL_INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "FTSE 100": "^FTSE",
    "Shanghai Composite": "000001.SS",
}

INDIA_INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
}

# Indicator settings
VWAP_RESET_TIME = "09:15"  # NSE market open, VWAP resets daily
RSI_PERIOD = 14
EMA_PERIODS = [9, 21, 50]
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
