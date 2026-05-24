"""阶段二：技术分析大师 — 读取 OHLCV + 指标 → 调用 LLM → 返回趋势/形态判断"""

from typing import List

import pandas as pd

from masters.base_master import BaseMaster, MasterOpinion
from masters.registry import STAGE2_MASTERS
import config


class TechnicalMaster(BaseMaster):
    """阶段二：趋势/形态/量价分析"""

    async def analyze(self, context: dict) -> MasterOpinion:
        symbol = context.get("symbol", "")
        price = context.get("current_price", 0)
        indicator_snapshot = context.get("indicator_snapshot", "")

        prompt = f"""你是一位技术分析大师 [{self.name}]，请基于以下框架和数据输出你的技术分析观点。

## 你的技术分析框架
{self.framework}

## 当前数据
股票：{symbol}
当前价格：{price}

## 技术指标快照（最近 5 个交易日）
{indicator_snapshot}

## 输出要求（严格 JSON）
{{
  "stance": "bullish" | "bearish" | "neutral",
  "confidence": 0.0~1.0,
  "reasoning": "完整的技术分析推理（至少200字），包含趋势判断、形态识别和关键价位分析",
  "trend_direction": "上升趋势" | "下降趋势" | "横盘整理",
  "pattern_identified": "识别到的技术形态",
  "support_level": 支撑位数值,
  "resistance_level": 阻力位数值,
  "signals": ["信号标签1", "信号标签2"],
  "risk_warning": "主要技术风险提示"
}}
"""
        result = await self._call_llm_json(prompt, timeout=config.STAGE2_TIMEOUT_SECONDS)

        support = result.get("support_level")
        resistance = result.get("resistance_level")
        key_levels = []
        if isinstance(support, (int, float)):
            key_levels.append(float(support))
        if isinstance(resistance, (int, float)):
            key_levels.append(float(resistance))

        return MasterOpinion(
            master_name=self.name,
            stage=2,
            stance=result.get("stance", "neutral"),
            confidence=float(result.get("confidence", 0.5)),
            reasoning=result.get("reasoning", ""),
            key_levels=key_levels,
            signals=result.get("signals", []),
            risk_warning=result.get("risk_warning", ""),
        )


# ── 工厂 ──────────────────────────────────────────────────────

def create_stage2_masters() -> List[TechnicalMaster]:
    """创建全部 12 位阶段二大师实例"""
    return [TechnicalMaster(name=n, stage=2, perspective_file=pf)
            for n, pf in STAGE2_MASTERS]


# ── 工具函数 ──────────────────────────────────────────────────

def build_indicator_snapshot(df: pd.DataFrame, tail: int = 5) -> str:
    """从指标 DataFrame 的最后 N 行构造人类可读文本供 LLM"""
    if df is None or df.empty:
        return "（技术指标数据暂缺）"
    recent = df.tail(tail)
    cols_of_interest = [c for c in recent.columns if c not in ("Date",)]
    lines = []
    for _, row in recent.iterrows():
        date_str = str(row.get("Date", ""))[:10]
        vals = " | ".join(
            f"{c}={row[c]:.2f}" if isinstance(row[c], float) else f"{c}={row[c]}"
            for c in cols_of_interest if pd.notna(row.get(c))
        )
        lines.append(f"{date_str}: {vals}")
    return "\n".join(lines)
