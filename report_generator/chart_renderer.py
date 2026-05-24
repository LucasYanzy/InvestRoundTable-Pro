"""技术图表渲染器 — mplfinance K线图 + 指标标注。"""

import os
import logging

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from data_engine.schema import DebateResult
import config

logger = logging.getLogger(__name__)


def render_chart(df: pd.DataFrame, result: DebateResult, output_dir: str) -> str:
    """
    绘制 K 线图 + 均线 + 成交量 + 大师标注
    返回图片文件路径
    """
    try:
        import mplfinance as mpf
    except ImportError:
        logger.warning("mplfinance 未安装，跳过图表生成")
        return ""

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{result.symbol}_{result.analysis_date.replace('-', '')}_chart.png"
    filepath = os.path.join(output_dir, filename)

    # 准备数据：mplfinance 需要 DatetimeIndex
    plot_df = df.tail(120).copy()   # 最近 120 根 K 线
    plot_df['Date'] = pd.to_datetime(plot_df['Date'])
    plot_df.set_index('Date', inplace=True)

    # 均线
    add_plots = []
    for col, color in [('SMA_20', 'blue'), ('SMA_50', 'orange'), ('SMA_200', 'red')]:
        if col in plot_df.columns:
            add_plots.append(mpf.make_addplot(plot_df[col].astype(float), color=color, width=0.8))

    # 布林带
    for col, color, ls in [('BBU_20_2.0', 'gray', '--'), ('BBL_20_2.0', 'gray', '--')]:
        if col in plot_df.columns:
            add_plots.append(mpf.make_addplot(plot_df[col].astype(float), color=color, linestyle=ls, width=0.5))

    # RSI 子图
    if 'RSI_14' in plot_df.columns:
        add_plots.append(mpf.make_addplot(plot_df['RSI_14'].astype(float), panel=2, color='purple', ylabel='RSI'))

    # MACD 子图
    for col in ['MACD_12_26_9', 'MACDs_12_26_9']:
        if col in plot_df.columns:
            add_plots.append(mpf.make_addplot(plot_df[col].astype(float), panel=3, color='green' if 'MACD_' in col else 'red', ylabel='MACD'))
    if 'MACDh_12_26_9' in plot_df.columns:
        macdh = plot_df['MACDh_12_26_9'].astype(float)
        colors = ['green' if v >= 0 else 'red' for v in macdh]
        add_plots.append(mpf.make_addplot(macdh, type='bar', panel=3, color=colors, width=0.7))

    # 支撑 / 阻力水平线
    hlines = {}
    s2 = result.stage2_result
    levels = []
    level_colors = []
    if s2.key_support:
        levels.append(s2.key_support)
        level_colors.append('green')
    if s2.key_resistance:
        levels.append(s2.key_resistance)
        level_colors.append('red')
    if levels:
        hlines = dict(hlines=levels, colors=level_colors, linestyle='-.', linewidths=1)

    # 标题
    bull_names = ', '.join(result.stage2_result.bullish_masters[:3]) or '无'
    bear_names = ', '.join(result.stage2_result.bearish_masters[:3]) or '无'
    title = f"{result.symbol} — {result.overall_consensus} (置信度 {result.overall_confidence:.0%})\n🟢 {bull_names}  |  🔴 {bear_names}"

    kwargs = dict(
        type='candle',
        style=config.CHART_STYLE,
        title=title,
        volume=True,
        addplot=add_plots if add_plots else None,
        figsize=(16, 10),
        savefig=filepath,
        tight_layout=True,
    )
    if hlines:
        kwargs['hlines'] = hlines

    try:
        mpf.plot(plot_df, **kwargs)
        logger.info("图表已保存: %s", filepath)
    except Exception as e:
        logger.error("图表生成失败: %s", e)
        filepath = ""

    plt.close('all')
    return filepath
