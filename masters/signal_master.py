"""阶段三：信号大师 — 读取定制指标数据包 → 输出信号方向+强度+价位"""

from typing import List

import pandas as pd

from masters.base_master import BaseMaster, MasterOpinion
from masters.registry import STAGE3_MASTERS
import config


class SignalMaster(BaseMaster):
    """阶段三信号大师：纯数字信号输出"""

    def __init__(self, name: str, stage: int, perspective_file: str,
                 indicator_keys: List[str]):
        super().__init__(name=name, stage=stage, perspective_file=perspective_file)
        self.indicator_keys = indicator_keys

    async def analyze(self, context: dict) -> MasterOpinion:
        symbol = context.get("symbol", "")
        price = context.get("current_price", 0)
        df: pd.DataFrame = context.get("df_indicators")
        indicator_text = self._extract_indicators(df)

        prompt = f"""你是一位技术指标大师 [{self.name}]，请基于以下框架和数据输出技术信号。

## 你的指标框架
{self.framework}

## 当前数据
股票：{symbol}
当前价格：{price}

指标数值：
{indicator_text}

## 输出要求（严格 JSON）
{{
  "signal_direction": "bullish" | "bearish" | "neutral",
  "signal_strength": 0-100,
  "support_level": 支撑位,
  "breakout_level": 突破位,
  "target_high": 目标价上限,
  "target_low": 目标价下限,
  "stop_loss": 止损位,
  "indicator_status": "指标状态描述（至少50字）",
  "market_condition": "当前市场环境说明"
}}
"""
        result = await self._call_llm_json(prompt, timeout=config.STAGE3_TIMEOUT_SECONDS)

        def _safe_float(v):
            try:
                return float(v) if v is not None else None
            except (ValueError, TypeError):
                return None

        return MasterOpinion(
            master_name=self.name,
            stage=3,
            stance=result.get("signal_direction", "neutral"),
            confidence=float(result.get("signal_strength", 50)) / 100.0,
            reasoning=result.get("indicator_status", ""),
            key_levels=[v for v in [_safe_float(result.get("support_level")),
                                     _safe_float(result.get("breakout_level"))] if v],
            signals=[result.get("market_condition", "")],
            risk_warning="",
            signal_strength=int(result.get("signal_strength", 50)),
            entry_target=_safe_float(result.get("breakout_level")),
            stop_loss=_safe_float(result.get("stop_loss")),
            target_high=_safe_float(result.get("target_high")),
            target_low=_safe_float(result.get("target_low")),
        )

    def _extract_indicators(self, df: pd.DataFrame) -> str:
        """从 DataFrame 最后一行提取本大师关注的指标"""
        if df is None or df.empty:
            return "（指标数据暂缺）"
        last = df.iloc[-1]
        lines = []
        for k in self.indicator_keys:
            val = last.get(k)
            if pd.notna(val):
                lines.append(f"- {k}: {val:.4f}" if isinstance(val, float) else f"- {k}: {val}")
            else:
                lines.append(f"- {k}: N/A")
        # 基础 OHLCV
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            v = last.get(c)
            if pd.notna(v):
                lines.append(f"- {c}: {v}")
        return "\n".join(lines)


# ── 工厂 ──────────────────────────────────────────────────────

def create_stage3_masters() -> List[SignalMaster]:
    """创建全部 11 位阶段三大师实例"""
    return [SignalMaster(name=n, stage=3, perspective_file=pf, indicator_keys=ik)
            for n, pf, ik in STAGE3_MASTERS]
