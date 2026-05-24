# System Architecture

## Overview

Investment Masters Roundtable is a multi-agent AI debate system that uses 37 specialized LLM-powered "masters" to analyze stocks across three complementary dimensions: fundamental value, technical trends, and quantitative signals.

## Architecture Diagram

```mermaid
graph TB
    subgraph CLI["CLI / Web Entry"]
        RUN["run.py"]
        FLASK["web_app/app.py"]
    end

    subgraph CONFIG["Configuration"]
        CFG["config.py"]
        ENV[".env"]
    end

    subgraph DE["Data Engine"]
        FET["fetcher.py<br/>yfinance + akshare"]
        FUN["fundamental_data.py<br/>PE/PB/ROE/Revenue"]
        TI["technical_indicators.py<br/>20+ indicators"]
        CA["cache.py<br/>LRU + File cache"]
        SCH["schema.py<br/>Data structures"]
    end

    subgraph MA["Masters Layer"]
        BM["base_master.py<br/>LLM call + fallback"]
        REG["registry.py<br/>37 master entries"]
        IM["investment_master.py<br/>Stage 1 factory"]
        TM["technical_master.py<br/>Stage 2 factory"]
        SM["signal_master.py<br/>Stage 3 factory"]
        SR["skill_references/<br/>37 framework files"]
    end

    subgraph DO["Debate Orchestrator"]
        ORC["orchestrator.py<br/>Main pipeline"]
        S1D["stage1_debate.py<br/>7-step debate"]
        S2A["stage2_analysis.py<br/>Parallel analysis"]
        S3S["stage3_signals.py<br/>Signal matrix"]
        CD["conflict_detector.py"]
        CSC["cross_stage_conflict.py"]
        CS["confidence_scorer.py"]
        AGG["aggregator.py<br/>60/20/20 weighted"]
    end

    subgraph RG["Report Generator"]
        MR["markdown_report.py"]
        HR["html_report.py"]
        CR["chart_renderer.py"]
    end

    RUN --> ORC
    FLASK --> ORC
    CFG --> ORC
    ENV --> CFG

    ORC --> FET
    ORC --> FUN
    FET --> CA
    FUN --> CA
    FET --> TI

    ORC --> S1D
    ORC --> S2A
    ORC --> S3S
    S1D --> IM --> BM
    S2A --> TM --> BM
    S3S --> SM --> BM
    BM --> SR
    BM --> REG

    S1D --> CD
    S3S --> CD
    ORC --> CSC
    ORC --> CS
    ORC --> AGG

    AGG --> MR
    AGG --> HR
    AGG --> CR
```

## Data Flow

### Stage Pipeline (Serial)

```
Stage 1 (60% weight)        Stage 2 (20% weight)        Stage 3 (20% weight)
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ 14 Investment     │        │ 12 Technical      │        │ 11 Signal        │
│ Masters           │ ────→ │ Masters           │ ────→ │ Masters          │
│                   │        │                   │        │                  │
│ Input: Fundament- │        │ Input: OHLCV +    │        │ Input: OHLCV +   │
│ als (PE/PB/ROE)   │        │ Tech Indicators   │        │ Indicator Values │
│                   │        │                   │        │                  │
│ Process:          │        │ Process:          │        │ Process:         │
│ 1. Independent    │        │ 1. Parallel       │        │ 1. Parallel      │
│    analysis       │        │    analysis       │        │    signal gen    │
│ 2. Camp division  │        │ 2. Consensus      │        │ 2. Conflict      │
│ 3. 2-round debate │        │    trend          │        │    detection     │
│ 4. Vote           │        │ 3. Key levels     │        │ 3. Debate        │
│                   │        │                   │        │ 4. Weighted vote │
│ Output:           │        │ Output:           │        │ Output:          │
│ Bull/Bear/Neutral │        │ Trend + S/R       │        │ Signal matrix +  │
│ + Debate record   │        │ levels            │        │ Net direction    │
└──────────────────┘        └──────────────────┘        └──────────────────┘
                                                                 │
                                                                 ▼
                                                    ┌──────────────────┐
                                                    │ Cross-Stage      │
                                                    │ Conflict Check   │
                                                    │ + 60/20/20 Agg   │
                                                    └──────────────────┘
```

### LLM Call Pattern

Each master's `analyze()` method:
1. Loads its skill framework from `skill_references/*.md`
2. Combines framework + market data into a prompt
3. Calls LLM with `response_format=json_object`
4. Parses response into `MasterOpinion` dataclass
5. Falls back to neutral opinion on any error

**Concurrency**: All masters within a stage run in parallel via `asyncio.gather()`. Stages execute serially.

## Extension Points

### Adding a New Master

1. Add entry to `masters/registry.py`
2. Create `masters/skill_references/{stage}/{name}-perspective.md`
3. Update count in `config.py`
4. The factory functions automatically pick up new registry entries

### Adding a New Market

1. Add market handler in `data_engine/fetcher.py`
2. Add fundamental data source in `data_engine/fundamental_data.py`
3. Add market option to CLI in `run.py`

### Custom LLM Backend

Set in `.env`:
```ini
LLM_API_BASE=https://your-api-endpoint.com/v1
LLM_API_KEY=your-key
LLM_MODEL=your-model-name
```

Any OpenAI-compatible API works out of the box.
