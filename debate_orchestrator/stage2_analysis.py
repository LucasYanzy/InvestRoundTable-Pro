"""阶段二：12 位技术分析大师并行分析"""

import logging

import asyncio
from typing import List
from masters.base_master import MasterOpinion
from masters.technical_master import create_stage2_masters, build_indicator_snapshot
from data_engine.schema import Stage2AnalysisResult


async def run_stage2_analysis(context: dict) -> Stage2AnalysisResult:
    """并行调用 12 位技术大师，整合趋势/形态/量价结果"""
    masters = create_stage2_masters()
    result = Stage2AnalysisResult()

    # 构造指标快照
    df = context.get("df_indicators")
    context["indicator_snapshot"] = build_indicator_snapshot(df, tail=5)

    tasks = [m.analyze(context) for m in masters]
    opinions: List[MasterOpinion] = await asyncio.gather(*tasks, return_exceptions=True)

    valid = []
    for op in opinions:
        if isinstance(op, Exception):
            logging.getLogger(__name__).warning("[Stage2] 大师分析异常: %s", op)
        else:
            valid.append(op)

    result.opinions = valid

    # 阵营划分
    supports = []
    resistances = []
    for op in valid:
        if op.stance == "bullish":
            result.bullish_masters.append(op.master_name)
        elif op.stance == "bearish":
            result.bearish_masters.append(op.master_name)
        else:
            result.neutral_masters.append(op.master_name)
        # 收集关键价位
        if len(op.key_levels) >= 1:
            supports.append(op.key_levels[0])
        if len(op.key_levels) >= 2:
            resistances.append(op.key_levels[1])

    # 取中位数作为共识支撑/阻力
    if supports:
        supports.sort()
        result.key_support = supports[len(supports) // 2]
    if resistances:
        resistances.sort()
        result.key_resistance = resistances[len(resistances) // 2]

    # 趋势总结
    total = len(valid)
    if total > 0:
        bull_ratio = len(result.bullish_masters) / total
        if bull_ratio > 0.5:
            result.trend_summary = "技术面整体偏多"
        elif bull_ratio < 0.3:
            result.trend_summary = "技术面整体偏空"
        else:
            result.trend_summary = "技术面信号混合"

    return result
