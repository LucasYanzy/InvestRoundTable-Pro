#!/usr/bin/env python3
"""
投资大师圆桌 (Investment Masters Roundtable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
31 位投资大师分三阶段分析你的股票。

Usage:
    python run.py --symbol AAPL --market US
    python run.py --symbol 000001 --market CN
    python run.py --symbol 0700.HK --market HK
    python run.py --web
"""

import argparse
import asyncio
import logging
import os
import sys

import config

# ── Logging ──────────────────────────────────────────────────

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
LOG_DATE_FMT = "%H:%M:%S"


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FMT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # 降低第三方库噪音
    for noisy in ("urllib3", "httpcore", "httpx", "openai", "yfinance", "matplotlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# ── CLI ──────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roundtable",
        description="31位大师三阶段圆桌辩论系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --symbol AAPL --market US        分析美股苹果
  %(prog)s --symbol 000001 --market CN      分析A股平安银行
  %(prog)s --symbol 0700.HK --market HK     分析港股腾讯
  %(prog)s --web                             启动 Web 界面
        """,
    )
    parser.add_argument("--symbol", "-s", type=str, help="股票代码")
    parser.add_argument("--market", "-m", type=str, default="US",
                        choices=["US", "CN", "HK"], help="市场 (default: US)")
    parser.add_argument("--period", type=str, default=config.DEFAULT_PERIOD,
                        help="数据周期 (default: 2y)")
    parser.add_argument("--web", action="store_true", help="启动 Web 界面")
    parser.add_argument("--output", "-o", type=str, default=config.OUTPUT_DIR,
                        help="报告输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")
    return parser


# ── 入口 ─────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    _setup_logging(verbose=args.verbose)
    logger = logging.getLogger("roundtable")

    if args.web:
        logger.info("正在启动 Web 界面 → http://127.0.0.1:5000")
        try:
            from web_app.app import app
            app.run(debug=True, port=5000)
        except ImportError as e:
            logger.error("启动 Web 界面失败: %s", e)
            sys.exit(1)
        return

    if not args.symbol:
        parser.error("--symbol 是必填项（除非使用 --web）")

    if not config.LLM_API_KEY:
        logger.warning("LLM_API_KEY 未配置，大师分析将使用降级模式")
        logger.warning("请在 .env 文件中设置 LLM_API_KEY")

    # 延迟导入（避免无依赖时首次 import 就崩溃）
    from debate_orchestrator.orchestrator import run_full_analysis
    from report_generator import generate_markdown_report, generate_html_report, render_chart
    from data_engine import fetch_ohlcv, calculate_all_indicators

    # 运行分析
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            run_full_analysis(args.symbol, args.market, args.period)
        )
    finally:
        loop.close()

    # 输出目录
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    date_str = result.analysis_date.replace("-", "")

    # 生成图表
    chart_path = ""
    try:
        df = fetch_ohlcv(args.symbol, args.market, args.period)
        df_ind = calculate_all_indicators(df)
        chart_path = render_chart(df_ind, result, output_dir)
    except Exception as e:
        logger.warning("图表生成失败: %s", e)

    # 生成 Markdown 报告
    md_report = generate_markdown_report(result)
    md_path = os.path.join(output_dir, f"{args.symbol}_{date_str}_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    # 生成 HTML 报告
    html_report = generate_html_report(result, chart_path)
    html_path = os.path.join(output_dir, f"{args.symbol}_{date_str}_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    # 摘要
    logger.info("━" * 50)
    logger.info("📝 Markdown 报告: %s", md_path)
    logger.info("🌐 HTML 报告:     %s", html_path)
    if chart_path:
        logger.info("📈 技术图表:      %s", chart_path)
    logger.info("✅ 分析完成！输出目录: %s", output_dir)
    logger.info("━" * 50)


if __name__ == "__main__":
    main()
