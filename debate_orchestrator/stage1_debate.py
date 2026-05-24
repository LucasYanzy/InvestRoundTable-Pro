"""阶段一辩论：14 位投资大师七步定性辩论流程"""

import logging

import asyncio
from typing import List
from masters.base_master import BaseMaster, MasterOpinion
from masters.investment_master import create_stage1_masters
from data_engine.schema import Stage1DebateResult, DebateExchange, Conflict
import config


async def run_stage1_debate(context: dict) -> Stage1DebateResult:
    """
    执行七步辩论流程：
    1. 数据校准  2. 独立估值  3. 阵营划分
    4. 辩论交锋  5. 投票统计  6. 概率加权  7. 最终判断
    """
    masters = create_stage1_masters()
    result = Stage1DebateResult()

    # ── Step 1 & 2: 并行独立分析 ──
    tasks = [m.analyze(context) for m in masters]
    opinions: List[MasterOpinion] = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤异常
    valid_opinions = []
    for op in opinions:
        if isinstance(op, Exception):
            logging.getLogger(__name__).warning("[Stage1] 大师分析异常: %s", op)
        else:
            valid_opinions.append(op)

    result.opinions = valid_opinions

    # ── Step 3: 阵营划分 ──
    for op in valid_opinions:
        if op.stance in ("bullish",):
            result.bullish_masters.append(op.master_name)
        elif op.stance in ("bearish", "avoid"):
            result.bearish_masters.append(op.master_name)
        else:
            result.neutral_masters.append(op.master_name)

    # ── Step 4: 辩论交锋（选取对立阵营代表进行交锋） ──
    debates, conflicts = await _run_debates(masters, valid_opinions, context)
    result.debates = debates
    result.conflicts = conflicts

    # ── Step 5-7: 投票与共识 ──
    total = len(valid_opinions)
    if total > 0:
        bull_pct = len(result.bullish_masters) / total
        bear_pct = len(result.bearish_masters) / total
        if bull_pct > 0.5:
            result.consensus = "多数看多"
        elif bear_pct > 0.5:
            result.consensus = "多数看空/回避"
        else:
            result.consensus = "观点分歧严重"

    # 保留分歧
    if result.bullish_masters and result.bearish_masters:
        result.dissent = (
            f"看多阵营（{', '.join(result.bullish_masters)}）"
            f" vs 看空/回避阵营（{', '.join(result.bearish_masters)}）存在分歧"
        )

    return result


async def _run_debates(masters: list, opinions: List[MasterOpinion],
                       context: dict) -> tuple:
    """选择关键分歧进行2轮辩论交锋"""
    debates = []
    conflicts = []

    # 找出最强看多 & 最强看空
    bulls = [op for op in opinions if op.stance == "bullish"]
    bears = [op for op in opinions if op.stance in ("bearish", "avoid")]

    if not bulls or not bears:
        return debates, conflicts

    # 按置信度排序，取最坚定的代表
    bulls.sort(key=lambda x: x.confidence, reverse=True)
    bears.sort(key=lambda x: x.confidence, reverse=True)

    champion_bull = bulls[0]
    champion_bear = bears[0]

    # 找到对应的 master 实例用于 LLM 辩论
    bull_master = next((m for m in masters if m.name == champion_bull.master_name), None)
    bear_master = next((m for m in masters if m.name == champion_bear.master_name), None)

    if not bull_master or not bear_master:
        return debates, conflicts

    # 2 轮交锋
    symbol = context.get("symbol", "")

    # Round 1: 看空挑战看多
    challenge_prompt = f"""在关于 {symbol} 的圆桌辩论中，{champion_bull.master_name} 表达了看多观点：

"{champion_bull.reasoning}"

你是 {champion_bear.master_name}，请从你的投资框架出发，对上述看多观点提出质疑和反驳。请用 JSON 格式回复：
{{"challenge": "你的质疑内容（至少150字，体现你的分析风格和逻辑）"}}
"""
    r1 = await bear_master._call_llm_json(challenge_prompt, timeout=30)
    debates.append(DebateExchange(
        speaker=champion_bear.master_name,
        content=r1.get("challenge", "（质疑生成失败）"),
        round_num=1
    ))

    # Round 2: 看多回应
    response_prompt = f"""在关于 {symbol} 的圆桌辩论中，{champion_bear.master_name} 对你的看多观点提出了质疑：

"{r1.get('challenge', '')}"

你是 {champion_bull.master_name}，请回应这一质疑，可以反质疑对方，也可以部分认同。请用 JSON 格式回复：
{{"response": "你的回应内容（至少150字，体现你的分析风格和逻辑）"}}
"""
    r2 = await bull_master._call_llm_json(response_prompt, timeout=30)
    debates.append(DebateExchange(
        speaker=champion_bull.master_name,
        content=r2.get("response", "（回应生成失败）"),
        round_num=2
    ))

    # 记录冲突
    conflicts.append(Conflict(
        party_a=champion_bull.master_name,
        party_b=champion_bear.master_name,
        topic=f"{symbol} 投资价值判断",
        party_a_stance="bullish",
        party_b_stance=champion_bear.stance,
        severity="high" if abs(champion_bull.confidence - champion_bear.confidence) < 0.2 else "medium"
    ))

    return debates, conflicts
