"""统一数据格式定义 — 覆盖三阶段辩论系统全部数据流转结构"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ────────────────────────────── 基础结构 ──────────────────────────────

@dataclass
class Conflict:
    """冲突记录"""
    party_a: str
    party_b: str
    topic: str
    party_a_stance: str
    party_b_stance: str
    resolution: str = ""          # 辩论后是否形成共识
    severity: str = "medium"      # low / medium / high


@dataclass
class DebateExchange:
    """单轮辩论交锋"""
    speaker: str
    content: str
    round_num: int = 1


# ────────────────────────────── 阶段一结果 ──────────────────────────────

@dataclass
class Stage1DebateResult:
    """阶段一：14 位投资大师定性辩论结果"""
    bullish_masters: List[str] = field(default_factory=list)
    bearish_masters: List[str] = field(default_factory=list)
    neutral_masters: List[str] = field(default_factory=list)
    opinions: List[Any] = field(default_factory=list)        # List[MasterOpinion]
    debates: List[DebateExchange] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    consensus: str = ""
    dissent: str = ""


# ────────────────────────────── 阶段二结果 ──────────────────────────────

@dataclass
class Stage2AnalysisResult:
    """阶段二：12 位技术分析大师趋势/形态/量价"""
    bullish_masters: List[str] = field(default_factory=list)
    bearish_masters: List[str] = field(default_factory=list)
    neutral_masters: List[str] = field(default_factory=list)
    opinions: List[Any] = field(default_factory=list)
    trend_summary: str = ""
    key_support: Optional[float] = None
    key_resistance: Optional[float] = None


# ────────────────────────────── 阶段三结果 ──────────────────────────────

@dataclass
class SignalEntry:
    """阶段三：单个大师的信号行"""
    master_name: str
    signal_direction: str      # bullish / bearish / neutral
    signal_strength: int       # 0-100
    support_level: Optional[float] = None
    breakout_level: Optional[float] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None
    stop_loss: Optional[float] = None
    indicator_status: str = ""
    market_condition: str = ""


@dataclass
class Stage3SignalResult:
    """阶段三：11 位技术指标大师信号 + 辩论 + 投票"""
    signals: List[SignalEntry] = field(default_factory=list)
    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    net_score: float = 0.0        # 加权净方向
    debates: List[DebateExchange] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    action_advice: str = ""


# ────────────────────────────── 最终聚合结果 ──────────────────────────────

@dataclass
class DebateResult:
    """三阶段辩论完整结果"""
    symbol: str
    market: str
    current_price: float
    analysis_date: str
    # 三阶段子结果
    stage1_result: Stage1DebateResult = field(default_factory=Stage1DebateResult)
    stage2_result: Stage2AnalysisResult = field(default_factory=Stage2AnalysisResult)
    stage3_result: Stage3SignalResult = field(default_factory=Stage3SignalResult)
    # 跨阶段
    cross_stage_conflicts: List[Conflict] = field(default_factory=list)
    overall_consensus: str = ""
    overall_confidence: float = 0.0
    action_recommendation: str = ""
    key_risk_factors: List[str] = field(default_factory=list)
