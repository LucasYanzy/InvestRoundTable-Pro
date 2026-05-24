"""阶段三：11 位技术指标大师 — 信号矩阵 + 冲突辩论 + 投票统计"""

import asyncio
import logging

from typing import List
from masters.base_master import MasterOpinion
from masters.signal_master import create_stage3_masters
from data_engine.schema import (
    Stage3SignalResult, SignalEntry, DebateExchange, Conflict
)
from .conflict_detector import detect_conflicts
import config


async def run_stage3_signals(context: dict) -> Stage3SignalResult:
    """
    执行流程：
    1. 数据分发  2. 独立输出  3. 冲突检测
    4. 定向辩论  5. 投票统计  6. 操作建议
    """
    masters = create_stage3_masters()
    result = Stage3SignalResult()

    # ── 1 & 2: 并行获取信号 ──
    tasks = [m.analyze(context) for m in masters]
    opinions: List[MasterOpinion] = await asyncio.gather(*tasks, return_exceptions=True)

    valid = []
    for op in opinions:
        if isinstance(op, Exception):
            logging.getLogger(__name__).warning("[Stage3] 信号异常: %s", op)
        else:
            valid.append(op)

    # 构建信号矩阵
    for op in valid:
        entry = SignalEntry(
            master_name=op.master_name,
            signal_direction=op.stance,
            signal_strength=op.signal_strength or 50,
            support_level=op.key_levels[0] if op.key_levels else None,
            breakout_level=op.entry_target,
            target_high=op.target_high,
            target_low=op.target_low,
            stop_loss=op.stop_loss,
            indicator_status=op.reasoning,
            market_condition=op.signals[0] if op.signals else "",
        )
        result.signals.append(entry)

        if op.stance == "bullish":
            result.bullish_count += 1
        elif op.stance == "bearish":
            result.bearish_count += 1
        else:
            result.neutral_count += 1

    # ── 3: 冲突检测 ──
    conflicts = detect_conflicts(valid)
    result.conflicts = conflicts

    # ── 4: 定向辩论（冲突对之间） ──
    if conflicts:
        debates = await _run_signal_debates(masters, valid, conflicts, context)
        result.debates = debates

    # ── 5: 投票统计 ──
    total_strength = sum(s.signal_strength for s in result.signals) or 1
    weighted_bull = sum(s.signal_strength for s in result.signals if s.signal_direction == "bullish")
    weighted_bear = sum(s.signal_strength for s in result.signals if s.signal_direction == "bearish")
    result.net_score = (weighted_bull - weighted_bear) / total_strength

    # ── 6: 操作建议 ──
    if result.net_score > 0.3:
        result.action_advice = "技术信号偏多，可考虑多头布局"
    elif result.net_score < -0.3:
        result.action_advice = "技术信号偏空，注意风险控制"
    else:
        result.action_advice = "技术信号混合，建议观望"

    return result


async def _run_signal_debates(masters, opinions, conflicts, context) -> List[DebateExchange]:
    """对冲突对进行定向辩论"""
    debates = []
    symbol = context.get("symbol", "")

    # 只取前2个最重要的冲突
    for conflict in conflicts[:2]:
        # 找到对应 master 实例
        master_a = next((m for m in masters if m.name == conflict.party_a), None)
        master_b = next((m for m in masters if m.name == conflict.party_b), None)
        op_a = next((o for o in opinions if o.master_name == conflict.party_a), None)
        op_b = next((o for o in opinions if o.master_name == conflict.party_b), None)

        if not all([master_a, master_b, op_a, op_b]):
            continue

        # Round 1: B 质疑 A
        prompt1 = f"""在 {symbol} 技术信号圆桌中，{conflict.party_a} 的信号为 {op_a.stance}（强度{op_a.signal_strength}），理由："{op_a.reasoning}"。
你是 {conflict.party_b}，你的信号为 {op_b.stance}（强度{op_b.signal_strength}）。请从你的指标框架出发质疑对方。
回复JSON: {{"challenge": "质疑内容（至少100字）"}}"""
        r1 = await master_b._call_llm_json(prompt1, timeout=20)
        debates.append(DebateExchange(speaker=conflict.party_b,
                                       content=r1.get("challenge", ""), round_num=1))

        # Round 2: A 回应
        prompt2 = f"""在 {symbol} 技术信号圆桌中，{conflict.party_b} 质疑你的看{op_a.stance}信号：
"{r1.get('challenge', '')}"
你是 {conflict.party_a}，请回应。
回复JSON: {{"response": "回应内容（至少100字）"}}"""
        r2 = await master_a._call_llm_json(prompt2, timeout=20)
        debates.append(DebateExchange(speaker=conflict.party_a,
                                       content=r2.get("response", ""), round_num=2))

    return debates
