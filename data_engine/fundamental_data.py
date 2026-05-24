"""基本面数据拉取 — yfinance + akshare 双源。"""

import logging
from datetime import datetime

import yfinance as yf
import akshare as ak

from .cache import global_cache
import config

logger = logging.getLogger(__name__)

def fetch_fundamental_yfinance(symbol: str, market: str) -> dict:
    """使用 yfinance 获取基本面数据"""
    yf_symbol = symbol
    if market == 'HK' and not symbol.endswith('.HK'):
        yf_symbol = f"{symbol}.HK"
    elif market == 'CN':
        yf_symbol = f"{symbol}.SS" if symbol.startswith('6') else f"{symbol}.SZ"
        
    ticker = yf.Ticker(yf_symbol)
    info = ticker.info
    
    return {
        "Valuation": {
            "PE_TTM": info.get("trailingPE"),
            "Forward_PE": info.get("forwardPE"),
            "PB": info.get("priceToBook"),
            "PS": info.get("priceToSalesTrailing12Months"),
            "EV_EBITDA": info.get("enterpriseToEbitda"),
            "Dividend_Yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
            "Market_Cap": info.get("marketCap")
        },
        "Financials": {
            "ROE": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None,
            "ROA": info.get("returnOnAssets", 0) * 100 if info.get("returnOnAssets") else None,
            "Gross_Margin": info.get("grossMargins", 0) * 100 if info.get("grossMargins") else None,
            "Net_Margin": info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None,
            "Debt_to_Equity": info.get("debtToEquity"),
            "Revenue_Growth": info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else None,
            "Earnings_Growth": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else None
        },
        "Industry": {
            "Sector": info.get("sector"),
            "Industry": info.get("industry")
        }
    }

def fetch_fundamental_akshare_a(symbol: str) -> dict:
    """使用 akshare 获取 A股 基本面数据"""
    data = {
        "Valuation": {},
        "Financials": {},
        "Industry": {}
    }
    
    try:
        # 获取个股估值指标 (以 000001 为例)
        # 注意: 这里的接口需要具体匹配akshare最新API，用 stock_a_lg_indicator (乐咕乐蜀) 或 stock_zh_a_spot_em (东方财富实时)
        spot_df = ak.stock_zh_a_spot_em()
        row = spot_df[spot_df["代码"] == symbol]
        if not row.empty:
            data["Valuation"]["PE_TTM"] = row.iloc[0].get("市盈率-动态", None)
            data["Valuation"]["PB"] = row.iloc[0].get("市净率", None)
            data["Valuation"]["Market_Cap"] = row.iloc[0].get("总市值", None)
            data["Industry"]["Sector"] = row.iloc[0].get("所属行业", None)
            
        # 财务摘要 (同花顺)
        # 简化处理，实际中可以使用 stock_financial_abstract_ths
        # 如果 akshare 调用失败，数据字典会保持为空，供 LLM 提示
    except Exception as e:
        logger.warning("akshare基本面获取部分失败: %s", e)
        
    return data

def fetch_fundamental_data(symbol: str, market: str) -> dict:
    """统一的基本面获取入口"""
    today_str = datetime.now().strftime("%Y%m%d")
    cache_key = f"fund_{symbol}_{market}_{today_str}"
    
    cached_data = global_cache.get(cache_key, is_fundamental=True)
    if cached_data:
        return cached_data
        
    data = {}
    if market == 'CN':
        data = fetch_fundamental_akshare_a(symbol)
        # 尝试用 yfinance 补充 A 股
        try:
            yf_data = fetch_fundamental_yfinance(symbol, market)
            if yf_data.get("Valuation", {}).get("PE_TTM"):
                data["Valuation"].update(yf_data["Valuation"])
            if yf_data.get("Financials", {}).get("ROE"):
                data["Financials"].update(yf_data["Financials"])
        except:
            pass
    else:
        try:
            data = fetch_fundamental_yfinance(symbol, market)
        except Exception as e:
            logger.warning("yfinance基本面获取失败: %s", e)
            
    if data:
        global_cache.set(cache_key, data)
        
    return data
