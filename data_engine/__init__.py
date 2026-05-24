"""data_engine — 数据层（双轨：技术数据 + 基本面数据）

公共 API:
    fetch_ohlcv(symbol, market, period, interval) → DataFrame
    fetch_fundamental_data(symbol, market)         → dict
    calculate_all_indicators(df)                   → DataFrame
"""

from data_engine.fetcher import fetch_ohlcv
from data_engine.fundamental_data import fetch_fundamental_data
from data_engine.technical_indicators import calculate_all_indicators

__all__ = [
    "fetch_ohlcv",
    "fetch_fundamental_data",
    "calculate_all_indicators",
]
