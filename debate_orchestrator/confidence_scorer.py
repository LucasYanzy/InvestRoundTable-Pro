"""置信度评分器"""

from data_engine.schema import Stage1DebateResult, Stage2AnalysisResult, Stage3SignalResult
import config


def compute_overall_confidence(
    stage1: Stage1DebateResult,
    stage2: Stage2AnalysisResult,
    stage3: Stage3SignalResult,
) -> float:
    """加权计算综合置信度 (0~1)"""

    # 阶段一置信度：基于大师共识度
    total_s1 = len(stage1.bullish_masters) + len(stage1.bearish_masters) + len(stage1.neutral_masters)
    if total_s1 > 0:
        majority = max(len(stage1.bullish_masters), len(stage1.bearish_masters), len(stage1.neutral_masters))
        s1_conf = majority / total_s1
    else:
        s1_conf = 0.5

    # 阶段一大师个体置信度均值
    if stage1.opinions:
        s1_avg_conf = sum(op.confidence for op in stage1.opinions) / len(stage1.opinions)
        s1_conf = (s1_conf + s1_avg_conf) / 2

    # 阶段二置信度：类似
    total_s2 = len(stage2.bullish_masters) + len(stage2.bearish_masters) + len(stage2.neutral_masters)
    if total_s2 > 0:
        majority = max(len(stage2.bullish_masters), len(stage2.bearish_masters), len(stage2.neutral_masters))
        s2_conf = majority / total_s2
    else:
        s2_conf = 0.5

    if stage2.opinions:
        s2_avg_conf = sum(op.confidence for op in stage2.opinions) / len(stage2.opinions)
        s2_conf = (s2_conf + s2_avg_conf) / 2

    # 阶段三置信度：基于净分数的绝对值
    s3_conf = min(abs(stage3.net_score) + 0.3, 1.0)

    # 加权
    overall = (
        config.STAGE1_WEIGHT * s1_conf +
        config.STAGE2_WEIGHT * s2_conf +
        config.STAGE3_WEIGHT * s3_conf
    )

    return round(min(max(overall, 0.0), 1.0), 3)
