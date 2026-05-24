"""HTML 可视化报告生成器"""

import base64
import os
from data_engine.schema import DebateResult


def generate_html_report(result: DebateResult, chart_path: str = "") -> str:
    """生成 Bootstrap 风格 HTML 报告"""
    s1 = result.stage1_result
    s2 = result.stage2_result
    s3 = result.stage3_result

    # 嵌入图表
    chart_b64 = ""
    if chart_path and os.path.exists(chart_path):
        with open(chart_path, 'rb') as f:
            chart_b64 = base64.b64encode(f.read()).decode()

    # 信号矩阵行
    signal_rows = ""
    for s in s3.signals:
        color = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#a3a3a3"}.get(s.signal_direction, "#a3a3a3")
        support = f"{s.support_level:.2f}" if s.support_level else "-"
        breakout = f"{s.breakout_level:.2f}" if s.breakout_level else "-"
        target = f"{s.target_low:.2f}~{s.target_high:.2f}" if s.target_low and s.target_high else "-"
        stop = f"{s.stop_loss:.2f}" if s.stop_loss else "-"
        signal_rows += f"""<tr>
            <td>{s.master_name}</td>
            <td style="color:{color};font-weight:bold">{s.signal_direction}</td>
            <td><div class="progress-bar" style="width:{s.signal_strength}%">{s.signal_strength}</div></td>
            <td>{support}</td><td>{breakout}</td><td>{target}</td><td>{stop}</td>
        </tr>"""

    # 阶段一大师卡片
    s1_cards = ""
    for op in s1.opinions:
        color = {"bullish": "#22c55e", "bearish": "#ef4444", "avoid": "#ef4444", "neutral": "#eab308"}.get(op.stance, "#a3a3a3")
        s1_cards += f"""<div class="master-card" style="border-left:4px solid {color}">
            <h4>{op.master_name} — <span style="color:{color}">{op.stance}</span> | {op.confidence:.0%}</h4>
            <p>{op.reasoning[:500]}{'...' if len(op.reasoning) > 500 else ''}</p>
            {f'<p class="risk">⚠️ {op.risk_warning}</p>' if op.risk_warning else ''}
        </div>"""

    # 跨阶段冲突
    conflict_html = ""
    if result.cross_stage_conflicts:
        for c in result.cross_stage_conflicts:
            conflict_html += f"""<div class="conflict-card">
                <strong>{c.topic}</strong><br>
                {c.party_a} vs {c.party_b}<br>
                <em>{c.resolution}</em>
            </div>"""

    # 投票饼图（纯CSS）
    total_s1 = max(len(s1.bullish_masters) + len(s1.bearish_masters) + len(s1.neutral_masters), 1)
    bull_pct = len(s1.bullish_masters) / total_s1 * 100
    bear_pct = len(s1.bearish_masters) / total_s1 * 100

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>圆桌纪要 — {result.symbol} {result.analysis_date}</title>
<meta name="description" content="31位投资大师三阶段圆桌辩论分析报告 — {result.symbol}">
<style>
:root {{
    --bg: #0f172a; --surface: #1e293b; --card: #334155;
    --text: #e2e8f0; --dim: #94a3b8; --accent: #3b82f6;
    --green: #22c55e; --red: #ef4444; --yellow: #eab308;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--text); font-family:'Inter',sans-serif; line-height:1.6; }}
.container {{ max-width:1200px; margin:0 auto; padding:2rem; }}
h1 {{ font-size:2rem; margin-bottom:0.5rem; background:linear-gradient(135deg,var(--accent),#8b5cf6);
     -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
h2 {{ font-size:1.4rem; margin:2rem 0 1rem; border-bottom:1px solid var(--card); padding-bottom:0.5rem; }}
.hero {{ background:var(--surface); border-radius:12px; padding:2rem; margin-bottom:2rem;
         border:1px solid var(--card); }}
.hero .verdict {{ font-size:1.5rem; font-weight:700; }}
.hero .conf {{ color:var(--dim); font-size:0.9rem; }}
.stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin:1rem 0; }}
.stat {{ background:var(--card); border-radius:8px; padding:1rem; text-align:center; }}
.stat .num {{ font-size:1.8rem; font-weight:700; }}
.stat .label {{ color:var(--dim); font-size:0.8rem; }}
table {{ width:100%; border-collapse:collapse; margin:1rem 0; }}
th,td {{ padding:0.6rem 0.8rem; text-align:left; border-bottom:1px solid var(--card); }}
th {{ color:var(--dim); font-size:0.85rem; text-transform:uppercase; }}
.progress-bar {{ background:var(--accent); color:#fff; padding:2px 8px; border-radius:4px;
                 display:inline-block; font-size:0.8rem; min-width:30px; text-align:center; }}
.master-card {{ background:var(--surface); border-radius:8px; padding:1rem; margin:0.5rem 0; }}
.master-card h4 {{ margin-bottom:0.5rem; }}
.master-card p {{ color:var(--dim); font-size:0.9rem; }}
.master-card .risk {{ color:var(--yellow); margin-top:0.5rem; }}
.conflict-card {{ background:#451a03; border:1px solid var(--yellow); border-radius:8px;
                   padding:1rem; margin:0.5rem 0; }}
.chart-img {{ width:100%; border-radius:8px; margin:1rem 0; }}
.footer {{ text-align:center; color:var(--dim); padding:2rem 0; font-size:0.8rem; }}
</style>
</head>
<body>
<div class="container">
    <h1>📊 31位大师三阶段圆桌辩论 — {result.symbol}</h1>
    <p style="color:var(--dim)">{result.analysis_date} | {result.market} | ¥{result.current_price:.2f}</p>

    <div class="hero">
        <div class="verdict" style="color:{'var(--green)' if '多' in result.overall_consensus else 'var(--red)' if '空' in result.overall_consensus else 'var(--yellow)'}">
            {result.overall_consensus}
        </div>
        <div class="conf">置信度 {result.overall_confidence:.0%} | 权重：基本面60% + 趋势20% + 信号20%</div>
        <p style="margin-top:1rem">{result.action_recommendation}</p>
    </div>

    <div class="stat-grid">
        <div class="stat"><div class="num" style="color:var(--green)">{len(s1.bullish_masters)}</div><div class="label">阶段一看多</div></div>
        <div class="stat"><div class="num" style="color:var(--red)">{len(s1.bearish_masters)}</div><div class="label">阶段一看空</div></div>
        <div class="stat"><div class="num" style="color:var(--green)">{s3.bullish_count}</div><div class="label">信号看涨</div></div>
        <div class="stat"><div class="num" style="color:var(--red)">{s3.bearish_count}</div><div class="label">信号看跌</div></div>
    </div>

    {'<img class="chart-img" src="data:image/png;base64,' + chart_b64 + '" alt="技术图表"/>' if chart_b64 else ''}

    <h2>🏛️ 阶段一：14 位投资大师</h2>
    {s1_cards}

    <h2>📈 阶段二：12 位技术分析大师</h2>
    <p>趋势：{s2.trend_summary} | 支撑：{s2.key_support or '-'} | 阻力：{s2.key_resistance or '-'}</p>

    <h2>⚡ 阶段三：11 位技术指标大师信号矩阵</h2>
    <table>
        <tr><th>大师</th><th>信号</th><th>强度</th><th>支撑</th><th>突破</th><th>目标</th><th>止损</th></tr>
        {signal_rows}
    </table>
    <p>净方向: {s3.net_score:+.2f} | {s3.action_advice}</p>

    {'<h2>⚠️ 跨阶段冲突</h2>' + conflict_html if conflict_html else ''}

    <h2>🚨 风险提示</h2>
    <ul>{''.join(f'<li>{r}</li>' for r in result.key_risk_factors) if result.key_risk_factors else '<li>暂无特殊风险</li>'}</ul>

    <div class="footer">
        本报告由 AI 系统自动生成，仅供参考，不构成投资建议。<br>
        31位大师三阶段圆桌辩论系统 © {result.analysis_date[:4]}
    </div>
</div>
</body>
</html>"""
    return html
