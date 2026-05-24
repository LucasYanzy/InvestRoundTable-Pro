"""主协调器：三阶段调度 + 数据准备 + 结果整合"""

import asyncio
import logging
from datetime import datetime

from data_engine.fetcher import fetch_ohlcv
from data_engine.fundamental_data import fetch_fundamental_data
from data_engine.technical_indicators import calculate_all_indicators
from data_engine.schema import DebateResult

from .stage1_debate import run_stage1_debate
from .stage2_analysis import run_stage2_analysis
from .stage3_signals import run_stage3_signals
from .aggregator import aggregate_results
import config

logger = logging.getLogger(__name__)


async def run_full_analysis(symbol: str, market: str,
                             period: str = None, interval: str = None) -> DebateResult:
    """
    完整三阶段分析流程入口。

    Pipeline:
        1. 拉取数据（OHLCV + 基本面）
        2. 预计算技术指标
        3. 阶段一 → 阶段二 → 阶段三（串行）
        4. 三阶段加权聚合

    Args:
        symbol: 股票代码（如 AAPL, 000001, 0700.HK）
        market: 市场代码（US / CN / HK）
        period: 数据周期（默认 config.DEFAULT_PERIOD）
        interval: K 线粒度（默认 config.DEFAULT_INTERVAL）

    Returns:
        DebateResult: 三阶段完整辩论结果
    """
    period = period or config.DEFAULT_PERIOD
    interval = interval or config.DEFAULT_INTERVAL
    analysis_date = datetime.now().strftime("%Y-%m-%d")

    logger.info("31位大师三阶段圆桌辩论 — %s (%s) %s", symbol, market, analysis_date)

    # ── 数据准备 ──────────────────────────────────────────────
    logger.info("[数据引擎] 拉取行情数据...")
    df = fetch_ohlcv(symbol, market, period, interval)
    logger.info("  行情数据: %d 根K线", len(df))

    logger.info("[数据引擎] 拉取基本面数据...")
    fundamental = fetch_fundamental_data(symbol, market)
    logger.info("  基本面数据就绪")

    logger.info("[数据引擎] 预计算技术指标...")
    df_indicators = calculate_all_indicators(df)
    indicator_cols = [c for c in df_indicators.columns if c not in df.columns]
    logger.info("  技术指标: %d 个", len(indicator_cols))

    current_price = float(df_indicators['Close'].iloc[-1])

    # 构建上下文（所有大师共享）
    context = {
        "symbol": symbol,
        "market": market,
        "current_price": current_price,
        "df": df,
        "df_indicators": df_indicators,
        "fundamental": fundamental,
    }

    # ── 阶段一：14 位投资大师 ─────────────────────────────────
    logger.info("[阶段一] 14 位投资大师定性辩论...")
    stage1 = await run_stage1_debate(context)
    logger.info("  看多: %d | 看空/回避: %d | 中立: %d — %s",
                len(stage1.bullish_masters), len(stage1.bearish_masters),
                len(stage1.neutral_masters), stage1.consensus)

    # ── 阶段二：12 位技术分析大师 ─────────────────────────────
    logger.info("[阶段二] 12 位技术分析大师趋势/形态分析...")
    stage2 = await run_stage2_analysis(context)
    logger.info("  看多: %d | 看空: %d | 中立: %d — %s",
                len(stage2.bullish_masters), len(stage2.bearish_masters),
                len(stage2.neutral_masters), stage2.trend_summary)

    # ── 阶段三：11 位技术信号大师 ─────────────────────────────
    logger.info("[阶段三] 11 位技术指标大师信号输出...")
    stage3 = await run_stage3_signals(context)
    logger.info("  看涨: %d | 看跌: %d | 中性: %d | 净方向: %+.2f",
                stage3.bullish_count, stage3.bearish_count,
                stage3.neutral_count, stage3.net_score)

    # ── 聚合 ─────────────────────────────────────────────────
    logger.info("[聚合器] 三阶段结果整合...")
    result = aggregate_results(
        symbol=symbol,
        market=market,
        current_price=current_price,
        analysis_date=analysis_date,
        stage1=stage1,
        stage2=stage2,
        stage3=stage3,
    )

    logger.info("综合判断: %s | 置信度: %.0f%%", result.overall_consensus,
                result.overall_confidence * 100)
    logger.info("操作建议: %s", result.action_recommendation)

    if result.cross_stage_conflicts:
        for c in result.cross_stage_conflicts:
            logger.warning("跨阶段冲突: %s — %s", c.topic, c.resolution)

    if result.key_risk_factors:
        for r in result.key_risk_factors:
            logger.warning("风险因素: %s", r)

    return result
