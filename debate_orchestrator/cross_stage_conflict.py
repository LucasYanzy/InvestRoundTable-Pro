"""跨阶段冲突检测 — 基本面 vs 技术面"""

from typing import List
from data_engine.schema import (
    Stage1DebateResult, Stage2AnalysisResult, Stage3SignalResult, Conflict
)


def detect_cross_stage_conflicts(
    stage1: Stage1DebateResult,
    stage2: Stage2AnalysisResult,
    stage3: Stage3SignalResult,
) -> List[Conflict]:
    """检测阶段一（基本面）与阶段二/三（技术面）的矛盾"""
    conflicts = []

    # 判断阶段一整体方向
    s1_bull = len(stage1.bullish_masters)
    s1_bear = len(stage1.bearish_masters)
    s1_direction = "bullish" if s1_bull > s1_bear else ("bearish" if s1_bear > s1_bull else "neutral")

    # 判断阶段二整体方向
    s2_bull = len(stage2.bullish_masters)
    s2_bear = len(stage2.bearish_masters)
    s2_direction = "bullish" if s2_bull > s2_bear else ("bearish" if s2_bear > s2_bull else "neutral")

    # 判断阶段三整体方向
    s3_direction = "bullish" if stage3.net_score > 0.2 else ("bearish" if stage3.net_score < -0.2 else "neutral")

    # 阶段一 vs 阶段二
    if s1_direction != "neutral" and s2_direction != "neutral" and s1_direction != s2_direction:
        conflicts.append(Conflict(
            party_a=f"阶段一（基本面 — {s1_direction}）",
            party_b=f"阶段二（技术趋势 — {s2_direction}）",
            topic="基本面与技术趋势方向分歧",
            party_a_stance=s1_direction,
            party_b_stance=s2_direction,
            severity="high",
            resolution="基本面看法与技术趋势出现矛盾，投资者需格外谨慎"
        ))

    # 阶段一 vs 阶段三
    if s1_direction != "neutral" and s3_direction != "neutral" and s1_direction != s3_direction:
        warning = ""
        if s1_direction == "bearish" and s3_direction == "bullish":
            warning = "⚠️ You are trading against Graham — 基本面大师看空，但技术信号看涨"
        elif s1_direction == "bullish" and s3_direction == "bearish":
            warning = "⚠️ 基本面支撑但技术信号走弱，注意短期回调风险"
        conflicts.append(Conflict(
            party_a=f"阶段一（基本面 — {s1_direction}）",
            party_b=f"阶段三（技术信号 — {s3_direction}）",
            topic="基本面与技术信号方向分歧",
            party_a_stance=s1_direction,
            party_b_stance=s3_direction,
            severity="high",
            resolution=warning
        ))

    # 阶段二 vs 阶段三
    if s2_direction != "neutral" and s3_direction != "neutral" and s2_direction != s3_direction:
        conflicts.append(Conflict(
            party_a=f"阶段二（趋势 — {s2_direction}）",
            party_b=f"阶段三（信号 — {s3_direction}）",
            topic="趋势判断与短期信号分歧",
            party_a_stance=s2_direction,
            party_b_stance=s3_direction,
            severity="medium",
            resolution="趋势与短期指标出现时间维度差异，需结合持仓周期判断"
        ))

    return conflicts
