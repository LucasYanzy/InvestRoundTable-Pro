"""冒烟测试 — 验证所有模块可以正确导入 + 工厂函数可以创建实例"""

import sys
import os

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_schema_imports():
    from data_engine.schema import (
        DebateResult, Stage1DebateResult, Stage2AnalysisResult,
        Stage3SignalResult, SignalEntry, Conflict, DebateExchange,
    )
    # 可以实例化
    result = DebateResult(symbol="TEST", market="US", current_price=100.0, analysis_date="2026-01-01")
    assert result.symbol == "TEST"
    print("✅ schema")


def test_base_master_imports():
    from masters.base_master import BaseMaster, MasterOpinion
    op = MasterOpinion(master_name="Test", stage=1, stance="neutral",
                       confidence=0.5, reasoning="test")
    assert op.master_name == "Test"
    print("✅ base_master")


def test_registry():
    from masters.registry import STAGE1_MASTERS, STAGE2_MASTERS, STAGE3_MASTERS
    assert len(STAGE1_MASTERS) == 14, f"Expected 14, got {len(STAGE1_MASTERS)}"
    assert len(STAGE2_MASTERS) == 12, f"Expected 12, got {len(STAGE2_MASTERS)}"
    assert len(STAGE3_MASTERS) == 11, f"Expected 11, got {len(STAGE3_MASTERS)}"
    print("✅ registry (14 + 12 + 11 = 37)")


def test_factories():
    from masters.investment_master import create_stage1_masters
    from masters.technical_master import create_stage2_masters
    from masters.signal_master import create_stage3_masters

    s1 = create_stage1_masters()
    s2 = create_stage2_masters()
    s3 = create_stage3_masters()
    assert len(s1) == 14
    assert len(s2) == 12
    assert len(s3) == 11
    print(f"✅ factories: {len(s1)} + {len(s2)} + {len(s3)} = {len(s1)+len(s2)+len(s3)} masters")


def test_package_level_imports():
    from masters import (
        create_stage1_masters, create_stage2_masters, create_stage3_masters,
        BaseMaster, MasterOpinion,
    )
    from data_engine import fetch_ohlcv, fetch_fundamental_data, calculate_all_indicators
    print("✅ package-level imports")


def test_orchestrator_imports():
    from debate_orchestrator import run_full_analysis
    from debate_orchestrator.stage1_debate import run_stage1_debate
    from debate_orchestrator.stage2_analysis import run_stage2_analysis
    from debate_orchestrator.stage3_signals import run_stage3_signals
    from debate_orchestrator.aggregator import aggregate_results
    print("✅ debate_orchestrator")


def test_report_imports():
    from report_generator import generate_markdown_report, generate_html_report, render_chart
    print("✅ report_generator")


def test_no_sys_path_hack():
    """确认项目中没有 sys.path.insert hack 残留"""
    import subprocess
    result = subprocess.run(
        ["grep", "-r", "sys.path.insert", "--include=*.py",
         "-l", "--exclude-dir=tests"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    found_files = [f for f in result.stdout.strip().split("\n") if f]
    assert not found_files, f"sys.path.insert hack found in: {found_files}"
    print("✅ no sys.path.insert hacks")


if __name__ == "__main__":
    test_schema_imports()
    test_base_master_imports()
    test_registry()
    test_factories()
    test_package_level_imports()
    test_orchestrator_imports()
    test_report_imports()
    test_no_sys_path_hack()
    print("\n🎉 All smoke tests passed!")
