import pandas as pd
import numpy as np

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False

def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算所有阶段二/阶段三所需的技术指标"""
    if df.empty or len(df) < 50:
        return df
        
    # 为了防止直接修改原始df，我们在副本上操作
    df = df.copy()
    
    if HAS_PANDAS_TA:
        _calc_with_pandas_ta(df)
    else:
        _calc_with_pure_pandas(df)

    # 自定义计算类（始终使用手写实现）
    _calc_elder_indicators(df)
    _calc_ichimoku(df)
    _calc_bill_williams(df)
    _calc_td_sequential(df)
    
    return df


def _calc_with_pandas_ta(df: pd.DataFrame):
    """使用 pandas-ta 库计算指标（推荐）"""
    df.ta.cores = 0
    # 均线
    df.ta.sma(length=5, append=True)
    df.ta.sma(length=10, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=100, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.ema(length=12, append=True)
    df.ta.ema(length=26, append=True)
    # 动量
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.stoch(high='High', low='Low', close='Close', k=9, d=3, smooth_k=3, append=True)
    df.ta.willr(length=14, append=True)
    df.ta.cci(length=20, append=True)
    df.ta.adx(length=14, append=True)
    # 波动
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.atr(length=14, append=True)
    df.ta.psar(append=True)
    # 量价
    df.ta.obv(append=True)
    df.ta.cmf(length=20, append=True)


def _calc_with_pure_pandas(df: pd.DataFrame):
    """纯 pandas/numpy 手工计算全部指标（pandas-ta 不可用时的降级方案）"""
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']

    # === 均线 ===
    for n in [5, 10, 20, 50, 100, 200]:
        df[f'SMA_{n}'] = close.rolling(window=n).mean()
    df['EMA_12'] = close.ewm(span=12, adjust=False).mean()
    df['EMA_26'] = close.ewm(span=26, adjust=False).mean()

    # === MACD ===
    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    df['MACD_12_26_9'] = ema_fast - ema_slow
    df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
    df['MACDh_12_26_9'] = df['MACD_12_26_9'] - df['MACDs_12_26_9']

    # === RSI ===
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # === KDJ (Stochastic) ===
    low9 = low.rolling(9).min()
    high9 = high.rolling(9).max()
    rsv = (close - low9) / (high9 - low9).replace(0, np.nan) * 100
    df['STOCHk_9_3_3'] = rsv.rolling(3).mean()
    df['STOCHd_9_3_3'] = df['STOCHk_9_3_3'].rolling(3).mean()

    # === Williams %R ===
    high14 = high.rolling(14).max()
    low14 = low.rolling(14).min()
    df['WILLR_14'] = (high14 - close) / (high14 - low14).replace(0, np.nan) * -100

    # === CCI ===
    tp = (high + low + close) / 3
    ma20 = tp.rolling(20).mean()
    md20 = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    df['CCI_20_0.015'] = (tp - ma20) / (0.015 * md20).replace(0, np.nan)

    # === ADX / DMI ===
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr14 = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    df['DMP_14'] = 100 * plus_dm.ewm(alpha=1/14, min_periods=14, adjust=False).mean() / atr14.replace(0, np.nan)
    df['DMN_14'] = 100 * minus_dm.ewm(alpha=1/14, min_periods=14, adjust=False).mean() / atr14.replace(0, np.nan)
    dx = (df['DMP_14'] - df['DMN_14']).abs() / (df['DMP_14'] + df['DMN_14']).replace(0, np.nan) * 100
    df['ADX_14'] = dx.ewm(alpha=1/14, min_periods=14, adjust=False).mean()

    # === Bollinger Bands ===
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df['BBU_20_2.0'] = sma20 + 2 * std20
    df['BBM_20_2.0'] = sma20
    df['BBL_20_2.0'] = sma20 - 2 * std20

    # === ATR ===
    df['ATRr_14'] = atr14

    # === OBV ===
    direction = np.where(close > close.shift(), 1, np.where(close < close.shift(), -1, 0))
    df['OBV'] = (volume * direction).cumsum()

    # === CMF ===
    mfm = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
    mfv = mfm * volume
    df['CMF_20'] = mfv.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)

def _calc_elder_indicators(df: pd.DataFrame):
    """亚历山大·埃尔德指标 (Force Index, Elder Ray)"""
    # Force Index = Volume * (Close - Close(prev))
    close_diff = df['Close'].diff()
    df['Force_Index_1'] = df['Volume'] * close_diff
    df['Force_Index_13'] = df['Force_Index_1'].ewm(span=13, adjust=False).mean()
    
    # Elder Ray: Bull Power / Bear Power
    ema13 = df['Close'].ewm(span=13, adjust=False).mean()
    df['Bull_Power'] = df['High'] - ema13
    df['Bear_Power'] = df['Low'] - ema13

def _calc_ichimoku(df: pd.DataFrame):
    """一目均衡表 (Ichimoku Kinko Hyo)"""
    # 转换线 (Tenkan-sen) - 9期最高最低的平均
    high9 = df['High'].rolling(window=9).max()
    low9 = df['Low'].rolling(window=9).min()
    df['Ichimoku_Tenkan'] = (high9 + low9) / 2
    
    # 基准线 (Kijun-sen) - 26期最高最低的平均
    high26 = df['High'].rolling(window=26).max()
    low26 = df['Low'].rolling(window=26).min()
    df['Ichimoku_Kijun'] = (high26 + low26) / 2
    
    # 先行带A (Senkou Span A)
    df['Ichimoku_SpanA'] = ((df['Ichimoku_Tenkan'] + df['Ichimoku_Kijun']) / 2).shift(26)
    
    # 先行带B (Senkou Span B) - 52期
    high52 = df['High'].rolling(window=52).max()
    low52 = df['Low'].rolling(window=52).min()
    df['Ichimoku_SpanB'] = ((high52 + low52) / 2).shift(26)
    
    # 迟行带 (Chikou Span)
    df['Ichimoku_Chikou'] = df['Close'].shift(-26)

def _calc_bill_williams(df: pd.DataFrame):
    """比尔·威廉姆斯 混沌操作法 (Alligator, AO, AC, Fractals)"""
    median_price = (df['High'] + df['Low']) / 2
    
    # 鳄鱼线 (Alligator) 
    # 颚线(Jaw) = 13期SMMA, 往前平移8
    df['Alligator_Jaw'] = median_price.rolling(window=13).mean().shift(8)
    # 齿线(Teeth) = 8期SMMA, 往前平移5
    df['Alligator_Teeth'] = median_price.rolling(window=8).mean().shift(5)
    # 唇线(Lips) = 5期SMMA, 往前平移3
    df['Alligator_Lips'] = median_price.rolling(window=5).mean().shift(3)
    
    # Awesome Oscillator (AO) = SMA(Median Price, 5) - SMA(Median Price, 34)
    ao = median_price.rolling(5).mean() - median_price.rolling(34).mean()
    df['AO'] = ao
    
    # Accelerator Oscillator (AC) = AO - SMA(AO, 5)
    df['AC'] = ao - ao.rolling(5).mean()

def _calc_td_sequential(df: pd.DataFrame):
    """托马斯·德马克 TD序列 (简化版 TD Setup)"""
    # TD Setup 9
    setup_up = np.zeros(len(df))
    setup_down = np.zeros(len(df))
    
    close = df['Close'].values
    
    for i in range(4, len(df)):
        if close[i] > close[i-4]:
            setup_up[i] = setup_up[i-1] + 1 if setup_up[i-1] > 0 else 1
            setup_down[i] = 0
        elif close[i] < close[i-4]:
            setup_down[i] = setup_down[i-1] + 1 if setup_down[i-1] > 0 else 1
            setup_up[i] = 0
        else:
            setup_up[i] = 0
            setup_down[i] = 0
            
    df['TD_Setup_Up'] = setup_up
    df['TD_Setup_Down'] = setup_down
