"""三阶段结果聚合 + 综合建议生成"""

from data_engine.schema import (
    DebateResult, Stage1DebateResult, Stage2AnalysisResult, Stage3SignalResult
)
from .confidence_scorer import compute_overall_confidence
from .cross_stage_conflict import detect_cross_stage_conflicts
import config


def aggregate_results(
    symbol: str,
    market: str,
    current_price: float,
    analysis_date: str,
    stage1: Stage1DebateResult,
    stage2: Stage2AnalysisResult,
    stage3: Stage3SignalResult,
) -> DebateResult:
    """三阶段加权聚合，生成最终 DebateResult"""

    # 跨阶段冲突
    cross_conflicts = detect_cross_stage_conflicts(stage1, stage2, stage3)

    # 综合置信度
    confidence = compute_overall_confidence(stage1, stage2, stage3)

    # ── 综合方向判断 ──
    # 阶段一方向 (权重 60%)
    s1_bull = len(stage1.bullish_masters)
    s1_bear = len(stage1.bearish_masters)
    s1_total = s1_bull + s1_bear + len(stage1.neutral_masters)
    s1_score = (s1_bull - s1_bear) / max(s1_total, 1)

    # 阶段二方向 (权重 20%)
    s2_bull = len(stage2.bullish_masters)
    s2_bear = len(stage2.bearish_masters)
    s2_total = s2_bull + s2_bear + len(stage2.neutral_masters)
    s2_score = (s2_bull - s2_bear) / max(s2_total, 1)

    # 阶段三方向 (权重 20%)
    s3_score = stage3.net_score

    # 加权总分 [-1, 1]
    total_score = (
        config.STAGE1_WEIGHT * s1_score +
        config.STAGE2_WEIGHT * s2_score +
        config.STAGE3_WEIGHT * s3_score
    )

    # 映射到建议
    if total_score > 0.3:
        consensus = "看多"
        action = f"综合建议：偏多操作，建议关注支撑位 {stage2.key_support or '待定'}，阻力位 {stage2.key_resistance or '待定'}"
    elif total_score < -0.3:
        consensus = "看空/回避"
        action = f"综合建议：偏空或观望，注意止损位设置，控制仓位"
    elif total_score > 0.1:
        consensus = "谨慎看多"
        action = f"综合建议：小仓位试探，突破 {stage2.key_resistance or '关键阻力'} 后可加仓，止损 {stage2.key_support or '支撑位'}"
    elif total_score < -0.1:
        consensus = "谨慎看空"
        action = f"综合建议：减仓观望，跌破 {stage2.key_support or '关键支撑'} 需果断止损"
    else:
        consensus = "观点分歧"
        action = "综合建议：多空分歧显著，建议观望等待方向明朗"

    # 风险因素
    risks = []
    if cross_conflicts:
        risks.append("基本面与技术面存在方向分歧")
    if stage3.neutral_count > stage3.bullish_count and stage3.neutral_count > stage3.bearish_count:
        risks.append("多数技术指标处于中性区间，趋势不明")
    if confidence < 0.5:
        risks.append("综合置信度偏低，判断可信度有限")
    if s1_bear > s1_bull and s1_bear > 5:
        risks.append("多数价值/宏观大师持回避态度")

    return DebateResult(
        symbol=symbol,
        market=market,
        current_price=current_price,
        analysis_date=analysis_date,
        stage1_result=stage1,
        stage2_result=stage2,
        stage3_result=stage3,
        cross_stage_conflicts=cross_conflicts,
        overall_consensus=consensus,
        overall_confidence=confidence,
        action_recommendation=action,
        key_risk_factors=risks,
    )
