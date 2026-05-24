"""Markdown 圆桌纪要报告生成器"""

from datetime import datetime
from data_engine.schema import DebateResult


def generate_markdown_report(result: DebateResult) -> str:
    """根据 DebateResult 生成完整 Markdown 圆桌纪要"""
    s1 = result.stage1_result
    s2 = result.stage2_result
    s3 = result.stage3_result

    lines = []
    lines.append(f"# 📊 31位大师三阶段圆桌会议纪要 — {result.symbol}")
    lines.append(f"")
    lines.append(f"> 分析日期：{result.analysis_date} | 市场：{result.market} | 当前价格：{result.current_price:.2f}")
    lines.append(f"")

    # ── 综合结论 ──
    lines.append(f"## 🎯 综合结论")
    lines.append(f"")
    lines.append(f"| 项目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| **综合判断** | {result.overall_consensus} |")
    lines.append(f"| **置信度** | {result.overall_confidence:.0%} |")
    lines.append(f"| **操作建议** | {result.action_recommendation} |")
    lines.append(f"| **权重分配** | 基本面 {60}% + 趋势 {20}% + 信号 {20}% |")
    lines.append(f"")

    # ── 阶段一 ──
    lines.append(f"---")
    lines.append(f"## 🏛️ 阶段一：14 位投资大师定性辩论")
    lines.append(f"")
    lines.append(f"### 投票结果")
    lines.append(f"| 观点 | 票数 | 大师 |")
    lines.append(f"|------|------|------|")
    lines.append(f"| 🟢 看多 | {len(s1.bullish_masters)} | {', '.join(s1.bullish_masters) or '无'} |")
    lines.append(f"| 🔴 看空/回避 | {len(s1.bearish_masters)} | {', '.join(s1.bearish_masters) or '无'} |")
    lines.append(f"| ⚪ 中立 | {len(s1.neutral_masters)} | {', '.join(s1.neutral_masters) or '无'} |")
    lines.append(f"")
    lines.append(f"**核心共识**：{s1.consensus}")
    if s1.dissent:
        lines.append(f"")
        lines.append(f"**保留分歧**：{s1.dissent}")
    lines.append(f"")

    # 各大师详细观点
    lines.append(f"### 详细观点")
    lines.append(f"")
    for op in s1.opinions:
        stance_emoji = {"bullish": "🟢", "bearish": "🔴", "avoid": "🔴", "neutral": "⚪"}.get(op.stance, "⚪")
        lines.append(f"<details>")
        lines.append(f"<summary>{stance_emoji} <b>{op.master_name}</b> — {op.stance} | 置信度 {op.confidence:.0%}</summary>")
        lines.append(f"")
        lines.append(f"{op.reasoning}")
        lines.append(f"")
        if op.risk_warning:
            lines.append(f"**⚠️ 风险提示**：{op.risk_warning}")
            lines.append(f"")
        lines.append(f"</details>")
        lines.append(f"")

    # 辩论交锋
    if s1.debates:
        lines.append(f"### 辩论交锋")
        lines.append(f"")
        for d in s1.debates:
            prefix = "🗣️ 质疑" if d.round_num == 1 else "💬 回应"
            lines.append(f"**{prefix} — {d.speaker}**")
            lines.append(f"")
            lines.append(f"> {d.content}")
            lines.append(f"")

    # ── 阶段二 ──
    lines.append(f"---")
    lines.append(f"## 📈 阶段二：12 位技术分析大师")
    lines.append(f"")
    lines.append(f"**趋势判断**：{s2.trend_summary}")
    if s2.key_support:
        lines.append(f"**关键支撑**：{s2.key_support:.2f}")
    if s2.key_resistance:
        lines.append(f"**关键阻力**：{s2.key_resistance:.2f}")
    lines.append(f"")
    lines.append(f"| 观点 | 票数 | 大师 |")
    lines.append(f"|------|------|------|")
    lines.append(f"| 🟢 看多 | {len(s2.bullish_masters)} | {', '.join(s2.bullish_masters) or '无'} |")
    lines.append(f"| 🔴 看空 | {len(s2.bearish_masters)} | {', '.join(s2.bearish_masters) or '无'} |")
    lines.append(f"| ⚪ 中立 | {len(s2.neutral_masters)} | {', '.join(s2.neutral_masters) or '无'} |")
    lines.append(f"")

    for op in s2.opinions:
        stance_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(op.stance, "⚪")
        levels = ""
        if op.key_levels:
            levels = f" | 关键价位: {', '.join(f'{l:.2f}' for l in op.key_levels)}"
        lines.append(f"<details>")
        lines.append(f"<summary>{stance_emoji} <b>{op.master_name}</b> — {op.stance} | 置信度 {op.confidence:.0%}{levels}</summary>")
        lines.append(f"")
        lines.append(f"{op.reasoning}")
        if op.risk_warning:
            lines.append(f"")
            lines.append(f"**⚠️ 风险**：{op.risk_warning}")
        lines.append(f"")
        lines.append(f"</details>")
        lines.append(f"")

    # ── 阶段三 ──
    lines.append(f"---")
    lines.append(f"## ⚡ 阶段三：11 位技术指标大师信号")
    lines.append(f"")
    lines.append(f"**信号矩阵**")
    lines.append(f"")
    lines.append(f"| 大师 | 信号 | 强度 | 支撑 | 突破 | 目标区间 | 止损 |")
    lines.append(f"|------|------|------|------|------|----------|------|")
    for s in s3.signals:
        emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(s.signal_direction, "⚪")
        support = f"{s.support_level:.2f}" if s.support_level else "-"
        breakout = f"{s.breakout_level:.2f}" if s.breakout_level else "-"
        target = f"{s.target_low:.2f}~{s.target_high:.2f}" if s.target_low and s.target_high else "-"
        stop = f"{s.stop_loss:.2f}" if s.stop_loss else "-"
        lines.append(f"| {s.master_name} | {emoji} {s.signal_direction} | {s.signal_strength} | {support} | {breakout} | {target} | {stop} |")
    lines.append(f"")
    lines.append(f"**投票统计**：看涨 {s3.bullish_count} 票 | 看跌 {s3.bearish_count} 票 | 中性 {s3.neutral_count} 票 | 净方向 {s3.net_score:+.2f}")
    lines.append(f"")
    lines.append(f"**操作建议**：{s3.action_advice}")
    lines.append(f"")

    # 阶段三辩论
    if s3.debates:
        lines.append(f"### 信号冲突辩论")
        lines.append(f"")
        for d in s3.debates:
            prefix = "🗣️ 质疑" if d.round_num == 1 else "💬 回应"
            lines.append(f"**{prefix} — {d.speaker}**")
            lines.append(f"")
            lines.append(f"> {d.content}")
            lines.append(f"")

    # ── 跨阶段冲突 ──
    if result.cross_stage_conflicts:
        lines.append(f"---")
        lines.append(f"## ⚠️ 跨阶段冲突检测")
        lines.append(f"")
        for i, c in enumerate(result.cross_stage_conflicts, 1):
            lines.append(f"{i}. **{c.topic}**")
            lines.append(f"   - {c.party_a} vs {c.party_b}")
            if c.resolution:
                lines.append(f"   - 🔔 {c.resolution}")
            lines.append(f"")

    # ── 风险提示 ──
    lines.append(f"---")
    lines.append(f"## 🚨 风险提示")
    lines.append(f"")
    if result.key_risk_factors:
        for r in result.key_risk_factors:
            lines.append(f"- {r}")
    else:
        lines.append(f"- 暂无特殊风险提示")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*本报告由 AI 系统自动生成，仅供参考，不构成投资建议。*")

    return "\n".join(lines)
