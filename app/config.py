"""
Central configuration: watchlist, API credentials, and constants.
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

WATCHLIST = [
    Stock("Larsen & Toubro", "LT", "NSE_EQ|INE018A01030"),
    Stock("ICICI Bank", "ICICIBANK", "NSE_EQ|INE090A01021"),
    Stock("Bharat Electronics", "BEL", "NSE_EQ|INE263A01024"),
    Stock("KPIT Technologies", "KPITTECH", "NSE_EQ|INE04I401011"),
    Stock("Persistent Systems", "PERSISTENT", "NSE_EQ|INE262H01021"),
    Stock("Solar Industries", "SOLARINDS", "NSE_EQ|INE343H01029"),
    Stock("Polycab India", "POLYCAB", "NSE_EQ|INE455K01017"),
    Stock("Apollo Hospitals", "APOLLOHOSP", "NSE_EQ|INE437A01024"),
    Stock("Info Edge", "NAUKRI", "NSE_EQ|INE663F01032"),
    Stock("Poly Medicure", "POLYMED", "NSE_EQ|INE205C01021"),
    Stock("ABB India", "ABB", "NSE_EQ|INE117A01022"),
    Stock("Bharat Forge", "BHARATFORG", "NSE_EQ|INE465A01025"),
    Stock("Trent", "TRENT", "NSE_EQ|INE849A01020"),
    Stock("Titan Company", "TITAN", "NSE_EQ|INE280A01028"),
    Stock("Kaynes Technology", "KAYNES", "NSE_EQ|INE918Z01012"),
    Stock("Dixon Technologies", "DIXON", "NSE_EQ|INE935N01020"),
    Stock("Hitachi Energy India", "POWERINDIA", "NSE_EQ|INE07Y701011"),
    Stock("PB Fintech", "POLICYBZR", "NSE_EQ|INE417T01026"),
    Stock("CDSL", "CDSL", "NSE_EQ|INE736A01011"),
    Stock("HBL Engineering", "HBLENGINE", "NSE_EQ|INE292B01021"),
    Stock("Azad Engineering", "AZAD", "NSE_EQ|INE02IJ01035"),
    Stock("Data Patterns", "DATAPATTNS", "NSE_EQ|INE0IX101010"),
    Stock("Zen Technologies", "ZENTEC", "NSE_EQ|INE251B01027"),
    Stock("MTAR Technologies", "MTARTECH", "NSE_EQ|INE864I01014"),
    Stock("Jyoti CNC Automation", "JYOTICNC", "NSE_EQ|INE980001024"),
    Stock("Clean Science & Technology", "CLEAN", "NSE_EQ|INE227W01023"),
    Stock("DOMS Industries", "DOMS", "NSE_EQ|INE321T01012"),
    Stock("Elecon Engineering", "ELECON", "NSE_EQ|INE205B01031"),
    Stock("Black Box", "BBOX", "NSE_EQ|INE676A01027"),
    Stock("Aether Industries", "AETHER", "NSE_EQ|INE0BWX01014"),
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
