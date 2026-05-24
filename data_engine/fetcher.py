import pandas as pd
import yfinance as yf
import akshare as ak
from datetime import datetime, timedelta
import pytz
import traceback
from .cache import global_cache

def parse_period_to_dates(period: str):
    """根据period（如 '2y', '6mo'）计算start_date和end_date"""
    end_date = datetime.now()
    if period.endswith('y'):
        years = int(period[:-1])
        start_date = end_date - timedelta(days=365*years)
    elif period.endswith('mo'):
        months = int(period[:-2])
        start_date = end_date - timedelta(days=30*months)
    elif period.endswith('d'):
        days = int(period[:-1])
        start_date = end_date - timedelta(days=days)
    else:
        # Default to 2 years
        start_date = end_date - timedelta(days=730)
    
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

def fetch_yfinance(symbol: str, market: str, period: str, interval: str) -> pd.DataFrame:
    """使用 yfinance 拉取数据"""
    yf_symbol = symbol
    if market == 'HK':
        # 港股在 yfinance 中的后缀通常是 .HK
        if not yf_symbol.endswith('.HK'):
            yf_symbol = f"{yf_symbol}.HK"
    elif market == 'CN':
        # A股在 yfinance 中的后缀是 .SS 或 .SZ
        if yf_symbol.startswith('6'):
            yf_symbol = f"{yf_symbol}.SS"
        else:
            yf_symbol = f"{yf_symbol}.SZ"
            
    df = yf.download(yf_symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"yfinance 返回空数据 for {yf_symbol}")
        
    # 重置索引，使得 Date 成为一列
    df = df.reset_index()
    # 列名可能具有多重索引(MultiIndex)，展开它
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # 重命名确保标准格式 Date/Open/High/Low/Close/Volume
    df.rename(columns={'Datetime': 'Date'}, inplace=True)
    
    # 统一转换时区到 Asia/Shanghai
    if pd.api.types.is_datetime64tz_dtype(df['Date']):
        df['Date'] = df['Date'].dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)
    
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()

def fetch_akshare_a(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """使用 akshare 拉取 A 股数据"""
    # 将 yfinance 的 interval 映射到 akshare 的 period
    interval_map = {'1d': 'daily', '1wk': 'weekly', '1mo': 'monthly'}
    ak_period = interval_map.get(interval, 'daily')
    
    start_date, end_date = parse_period_to_dates(period)
    
    df = ak.stock_zh_a_hist(symbol=symbol, period=ak_period, start_date=start_date, end_date=end_date, adjust="qfq")
    if df.empty:
        raise ValueError(f"akshare 返回空数据 for {symbol}")
        
    # akshare 列名映射
    # ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
    rename_map = {
        '日期': 'Date',
        '开盘': 'Open',
        '最高': 'High',
        '最低': 'Low',
        '收盘': 'Close',
        '成交量': 'Volume'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # 确保 Date 是 datetime 类型
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()

def fetch_ohlcv(symbol: str, market: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    统一的数据获取入口，支持缓存和自动降级
    """
    today_str = datetime.now().strftime("%Y%m%d")
    cache_key = f"{symbol}_{market}_{interval}_{period}_{today_str}"
    
    # 1. 查缓存
    cached_df = global_cache.get(cache_key)
    if cached_df is not None and not cached_df.empty:
        return cached_df
        
    df = None
    errors = []
    
    # 2. 拉取数据 (根据市场选择优先源)
    if market == 'CN':
        try:
            df = fetch_akshare_a(symbol, period, interval)
        except Exception as e:
            errors.append(f"akshare: {e}")
            try:
                df = fetch_yfinance(symbol, market, period, interval)
            except Exception as e:
                errors.append(f"yfinance: {e}")
    else:
        try:
            df = fetch_yfinance(symbol, market, period, interval)
        except Exception as e:
            errors.append(f"yfinance: {e}")
            if market == 'CN': # 仅A股支持akshare降级
                try:
                    df = fetch_akshare_a(symbol, period, interval)
                except Exception as e:
                    errors.append(f"akshare: {e}")
                    
    if df is None or df.empty:
        raise RuntimeError(f"无法拉取 {symbol} ({market}) 的行情数据。错误: {errors}")
        
    # 3. 数据清洗：确保类型正确
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['Close'], inplace=True)
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # 4. 写入缓存
    global_cache.set(cache_key, df)
    
    return df
