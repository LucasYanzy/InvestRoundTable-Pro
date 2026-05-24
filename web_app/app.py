"""Flask Web 应用 — 31位大师圆桌辩论系统"""

import os
import asyncio
from flask import Flask, render_template, request, jsonify

import config

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.form.get('symbol', '').strip()
    market = request.form.get('market', 'US')

    if not symbol:
        return jsonify({"error": "请输入股票代码"}), 400

    try:
        from debate_orchestrator.orchestrator import run_full_analysis
        from report_generator.markdown_report import generate_markdown_report
        from report_generator.html_report import generate_html_report
        from report_generator.chart_renderer import render_chart
        from data_engine.fetcher import fetch_ohlcv
        from data_engine.technical_indicators import calculate_all_indicators

        # 运行分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_full_analysis(symbol, market))
        loop.close()

        # 生成图表
        df = fetch_ohlcv(symbol, market)
        df_ind = calculate_all_indicators(df)
        chart_path = render_chart(df_ind, result, config.OUTPUT_DIR)

        # 生成报告
        md_report = generate_markdown_report(result)
        html_content = generate_html_report(result, chart_path)

        # 保存
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        date_str = result.analysis_date.replace('-', '')
        md_path = os.path.join(config.OUTPUT_DIR, f"{symbol}_{date_str}_report.md")
        html_path = os.path.join(config.OUTPUT_DIR, f"{symbol}_{date_str}_report.html")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_content

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
