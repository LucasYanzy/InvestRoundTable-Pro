"""冲突检测器 — 各阶段通用"""

from typing import List
from masters.base_master import MasterOpinion
from data_engine.schema import Conflict


def detect_conflicts(opinions: List[MasterOpinion]) -> List[Conflict]:
    """检测同阶段内观点对立的冲突对"""
    conflicts = []
    bulls = [op for op in opinions if op.stance == "bullish"]
    bears = [op for op in opinions if op.stance in ("bearish", "avoid")]

    # 两两配对：高置信度优先
    bulls.sort(key=lambda x: x.confidence, reverse=True)
    bears.sort(key=lambda x: x.confidence, reverse=True)

    paired = min(len(bulls), len(bears), 3)  # 最多3对
    for i in range(paired):
        severity = "high" if (bulls[i].confidence > 0.7 and bears[i].confidence > 0.7) else "medium"
        conflicts.append(Conflict(
            party_a=bulls[i].master_name,
            party_b=bears[i].master_name,
            topic=f"多空分歧 — {bulls[i].master_name} vs {bears[i].master_name}",
            party_a_stance=bulls[i].stance,
            party_b_stance=bears[i].stance,
            severity=severity,
        ))

    return conflicts
