"""阶段一：投资大师 — 读取基本面数据 → 调用 LLM → 返回定性观点"""

from typing import List

from masters.base_master import BaseMaster, MasterOpinion
from masters.registry import STAGE1_MASTERS
import config


class InvestmentMaster(BaseMaster):
    """阶段一投资大师：基本面分析"""

    async def analyze(self, context: dict) -> MasterOpinion:
        fundamental = context.get("fundamental", {})
        symbol = context.get("symbol", "")
        price = context.get("current_price", 0)

        prompt = f"""你是一位投资大师 [{self.name}]，请基于以下框架和数据输出你的投资观点。

## 你的投资框架
{self.framework}

## 当前数据
股票：{symbol}
当前价格：{price}

## 基本面数据
{format_fundamental(fundamental)}

## 输出要求（严格 JSON）
{{
  "stance": "bullish" | "bearish" | "neutral" | "avoid",
  "confidence": 0.0~1.0,
  "reasoning": "完整的分析推理（至少200字），包含你的核心依据、数据支撑和风险提示",
  "valuation_assessment": "对当前估值的判断",
  "key_risks": ["风险1", "风险2"],
  "signals": ["信号标签1", "信号标签2"],
  "risk_warning": "主要风险提示"
}}
"""
        result = await self._call_llm_json(prompt, timeout=config.STAGE1_TIMEOUT_SECONDS)

        return MasterOpinion(
            master_name=self.name,
            stage=1,
            stance=result.get("stance", "neutral"),
            confidence=float(result.get("confidence", 0.5)),
            reasoning=result.get("reasoning", ""),
            key_levels=[],
            signals=result.get("signals", []),
            risk_warning=result.get("risk_warning", ""),
            valuation={"assessment": result.get("valuation_assessment", ""),
                        "risks": result.get("key_risks", [])},
        )


# ── 工厂 ──────────────────────────────────────────────────────

def create_stage1_masters() -> List[InvestmentMaster]:
    """创建全部 14 位阶段一大师实例"""
    return [InvestmentMaster(name=name, stage=1, perspective_file=pf)
            for name, pf in STAGE1_MASTERS]


# ── 工具函数 ──────────────────────────────────────────────────

def format_fundamental(data: dict) -> str:
    """将基本面字典格式化为可读文本供 LLM 使用"""
    if not data:
        return "（基本面数据暂缺）"
    lines = []
    for section, values in data.items():
        if isinstance(values, dict):
            lines.append(f"\n### {section}")
            for k, v in values.items():
                if v is not None:
                    lines.append(f"- {k}: {v}")
    return "\n".join(lines) if lines else "（基本面数据暂缺）"
