# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-24

### Added
- **Three-stage architecture**: Fundamental debate → Technical analysis → Signal voting
- **37 investment masters**:
  - Stage 1: 14 value/growth/macro investment masters with 7-step debate process
  - Stage 2: 12 technical analysis masters with parallel trend/pattern analysis
  - Stage 3: 11 quantitative signal masters with signal matrix + conflict debate + voting
- **Multi-market support**: US stocks (yfinance), China A-shares (akshare), Hong Kong stocks
- **Data engine**:
  - OHLCV fetching with dual-source fallback
  - 20+ technical indicator pre-computation (pandas-ta + pure numpy)
  - Fundamental data (PE/PB/ROE/revenue)
  - 2-level caching (LRU memory + file pickle)
- **Debate orchestrator**:
  - Stage 1: 7-step qualitative debate (independent → camps → 2-round debate → vote)
  - Stage 2: Parallel technical analysis
  - Stage 3: Signal matrix → conflict detection → targeted debate → weighted vote
  - Cross-stage conflict detection ("You are trading against Graham")
  - 60/20/20 weighted aggregation
- **Report generation**:
  - Markdown roundtable minutes
  - Dark-themed HTML interactive report
  - mplfinance candlestick chart with overlays
- **Web interface**: Flask app with dark-themed SPA
- **CLI**: `python run.py --symbol AAPL --market US`
- **37 skill reference files**: Detailed investment/analysis frameworks for each master
- **GitHub Actions CI**: Multi-Python (3.9-3.12) lint + smoke test pipeline
