# 31位大师三阶段圆桌辩论系统 — 开发规格书

## 项目目标

构建一个**可实际运行**的三阶段多专家辩论系统，输入任意股票代码（A股/美股/港股），系统自动拉取真实行情数据，31位大师分三阶段分析，产出圆桌辩论纪要 + 技术图表 + 综合投资建议。

**三阶段架构**：
1. **阶段一**：14位投资大师（定性辩论）
2. **阶段二**：12位技术分析大师（趋势/形态/量价分析）
3. **阶段三**：11位技术指标大师（纯数字信号输出）

---

## 一、系统架构总览

```
用户输入（股票代码 + 市场）
    → [数据引擎] 双轨数据拉取：
         ├─ 技术数据轨：OHLCV + 预计算技术指标（服务于阶段二/三）
         └─ 基本面数据轨：财报 + 估值 + 行业对比（服务于阶段一）
    → [阶段一：14位投资大师] 定性辩论（价值投资/成长/宏观/逆向投资）
    → [阶段二：12位技术分析大师] 趋势/形态/量价分析（道氏/威科夫/艾略特/尼森/威尔德/阿佩尔/葛兰碧/德马克/莱恩/威廉姆斯/ARBR/埃尔德）
    → [阶段三：11位技术指标大师] 纯数字信号输出 + 冲突辩论 + 投票统计
    → [辩论协调器] 三阶段结果整合，跨阶段冲突检测，加权投票
    → [报告生成器] 输出 Markdown 圆桌纪要 + HTML 报告 + 技术图表
```

## 二、目录结构

```
technical-analysis-council/
├── README.md                 # 项目介绍、快速开始、演示截图
├── SPEC.md                   # 本文件：开发规格书
├── requirements.txt          # Python 依赖
├── run.py                    # 主入口：python run.py --symbol AAPL --market US
├── config.py                 # 全局配置（API密钥路径、缓存路径、模型选择）
│
├── data_engine/              # 数据层（双轨：技术数据 + 基本面数据）
│   ├── __init__.py
│   ├── fetcher.py            # 混合数据源调度（yfinance + akshare + 财报数据源）
│   ├── technical_indicators.py  # 技术指标预计算引擎（MA/RSI/MACD/KDJ/W%R/OBV/TD序列/力指数等）
│   ├── fundamental_data.py   # 基本面数据引擎（财报/估值/行业对比/机构持仓）
│   ├── cache.py              # 本地文件/内存二级缓存
│   └── schema.py             # 统一数据格式定义
│
├── masters/                  # 31位大师分析模块（三阶段）
│   ├── __init__.py
│   ├── base_master.py        # 大师基类（定义输入输出接口）
│   │
│   ├── stage1/               # 阶段一：14位投资大师（定性辩论）
│   │   ├── __init__.py
│   │   ├── value_master.py   # 价值投资类型基类
│   │   ├── growth_master.py  # 成长投资类型基类
│   │   ├── macro_master.py   # 宏观投资类型基类
│   │   ├── warren_buffett.py
│   │   ├── charlie_munger.py
│   │   ├── benjamin_graham.py
│   │   ├── peter_lynch.py
│   │   ├── howard_marks.py
│   │   ├── cathie_wood.py
│   │   ├── george_soros.py
│   │   ├── ray_dalio.py
│   │   ├── duan_yongping.py
│   │   ├── zhang_lei.py
│   │   ├── li_lu.py
│   │   ├── feng_liu.py
│   │   ├── qiu_guolu.py
│   │   └── lin_yuan.py
│   │
│   ├── stage2/               # 阶段二：12位技术分析大师（趋势/形态/量价）
│   │   ├── __init__.py
│   │   ├── charles_dow.py
│   │   ├── richard_wyckoff.py
│   │   ├── ralph_elliott.py
│   │   ├── steve_nison.py
│   │   ├── welles_wilder.py
│   │   ├── gerald_appel.py
│   │   ├── joseph_granville.py
│   │   ├── thomas_demark.py
│   │   ├── george_lane.py
│   │   ├── larry_williams.py
│   │   ├── alexander_elder.py
│   │   └── arbr_team.py
│   │
│   ├── stage3/               # 阶段三：11位技术指标大师（纯数字信号）
│   │   ├── __init__.py
│   │   ├── gerald_appel_signal.py     # MACD信号
│   │   ├── john_bollinger_signal.py   # 布林带信号
│   │   ├── joseph_granville_signal.py # MA+OBV信号
│   │   ├── goichi_hosoda_signal.py    # 一目均衡信号
│   │   ├── welles_wilder_signal.py    # RSI/DMI/ADX/ATR/PSAR信号
│   │   ├── george_lane_signal.py      # KDJ信号
│   │   ├── donald_lambert_signal.py   # CCI信号
│   │   ├── larry_williams_signal.py   # W%R信号
│   │   ├── marc_chaikin_signal.py     # CMF信号
│   │   ├── alexander_elder_signal.py  # 三重滤网信号
│   │   └── bill_williams_signal.py    # 混沌操作信号
│   │
│   └── skill_references/     # 31位大师的完整Skill框架文本（供LLM prompt使用）
│       ├── investment_masters/      # 阶段一 14个
│       │   ├── warren-buffett-perspective.md
│       │   ├── charlie-munger-perspective.md
│       │   ├── graham-perspective.md
│       │   ├── peterlynch-perspective.md
│       │   ├── howard-marks-perspective.md
│       │   ├── cathie-wood-perspective.md
│       │   ├── soros-perspective.md
│       │   ├── dalio-perspective.md
│       │   ├── duanyongping-perspective.md
│       │   ├── zhanglei-perspective.md
│       │   ├── lilu-perspective.md
│       │   ├── fengliu-perspective.md
│       │   ├── qiuguolu-perspective.md
│       │   └── linyuan-perspective.md
│       ├── technical_masters/       # 阶段二 12个
│       │   ├── charles-dow-perspective.md
│       │   ├── richard-wyckoff-perspective.md
│       │   ├── ralph-elliott-perspective.md
│       │   ├── steve-nison-perspective.md
│       │   ├── welles-wilder-perspective.md
│       │   ├── gerald-appel-perspective.md
│       │   ├── joseph-granville-perspective.md
│       │   ├── thomas-demark-perspective.md
│       │   ├── george-lane-perspective.md
│       │   ├── larry-williams-perspective.md
│       │   ├── alexander-elder-perspective.md
│       │   └── japanese-sentiment-indicators-perspective.md
│       └── signal_masters/          # 阶段三 11个（待创建）
│
├── debate_orchestrator/      # 辩论协调层（三阶段编排）
│   ├── __init__.py
│   ├── orchestrator.py       # 主协调器：三阶段调度、收集结果
│   ├── stage1_debate.py      # 阶段一：14人定性辩论（七步辩论流程）
│   ├── stage2_analysis.py    # 阶段二：12人技术分析（趋势/形态/量价）
│   ├── stage3_signals.py     # 阶段三：11人技术信号 + 冲突辩论 + 投票
│   ├── cross_stage_conflict.py  # 跨阶段冲突检测（基本面 vs 技术面）
│   ├── conflict_detector.py  # 观点冲突检测（多空分歧、指标矛盾）
│   ├── confidence_scorer.py  # 置信度评分
│   └── aggregator.py         # 三阶段结果聚合 + 综合建议生成
│
├── report_generator/         # 报告生成层
│   ├── __init__.py
│   ├── markdown_report.py    # Markdown 圆桌纪要模板
│   ├── html_report.py        # HTML 可视化报告（含图表嵌入）
│   └── chart_renderer.py     # matplotlib/mplfinance 技术图表渲染
│
├── web_app/                  # Web 界面（Flask + 前端）
│   ├── app.py                # Flask 主应用
│   ├── templates/
│   │   └── index.html        # 主页面：输入框 + 报告展示区
│   └── static/
│       └── style.css
│
├── tests/                    # 测试
│   ├── test_data_engine.py
│   ├── test_stage1_masters.py
│   ├── test_stage2_masters.py
│   ├── test_stage3_signals.py
│   └── test_orchestrator.py
│
├── examples/                 # 示例产出
│   ├── AAPL_20240523_report.md
│   └── TSLA_20240523_report.md
│
└── docs/                     # 技术文档
    ├── architecture.md
    ├── 2026-05-23-technical-signal-roundtable-design.md         # 阶段三设计
    └── 2026-05-23-technical-signal-roundtable-implementation-plan.md  # 阶段三实现计划
```

## 三、核心模块详细规格

### 3.1 数据引擎 (`data_engine/`)

#### `fetcher.py` — 混合数据源调度
- **输入**：`symbol`, `market`（US/HK/CN）, `period`（默认2y）, `interval`（默认1d）
- **数据源策略**：
  - 美股/港股 → `yfinance`（yf.download）
  - A股 → `akshare`（ak.stock_zh_a_hist）
  - 失败降级：yfinance失败时尝试akshare，反之亦然
- **输出**：统一格式的 Pandas DataFrame（列：Date/Open/High/Low/Close/Volume）
- **特殊处理**：
  - yfinance 默认返回 UTC 时间，需转换为 Asia/Shanghai
  - akshare 返回中文列名，需映射为英文标准列名
  - 自动处理复权（yfinance: auto_adjust=True；akshare: adjust="qfq"）

#### `technical_indicators.py` — 技术指标预计算引擎
- **输入**：OHLCV DataFrame
- **输出**：在原始 DataFrame 上追加所有标准指标列
- **需计算的指标**（按三个阶段共同需求覆盖）：

| 指标 | 参数 | 使用大师 | 计算库 |
|------|------|---------|--------|
| SMA 5/10/20/50/100/200 | — | 道/威科夫/艾略特 | pandas rolling |
| EMA 12/26 | — | 阿佩尔(MACD) | pandas ewm |
| MACD | 12/26/9 | 阿佩尔 | talib/pandas |
| RSI | 14 | 威尔德 | talib |
| KDJ (%K/%D) | 9/3/3 | 莱恩 | talib |
| W%R | 14 | 威廉姆斯 | talib |
| OBV | — | 葛兰碧 | talib |
| ATR | 14 | 威尔德 | talib |
| Bollinger Bands | 20/2 | 布林格(阶段三) | talib |
| CCI | 20 | 兰伯特(阶段三) | talib |
| ADX/DMI | 14 | 威尔德 | talib |
| CMF | 20 | 柴金(阶段三) | talib |
| PSAR | — | 威尔德 | talib |
| Force Index | 13 | 埃尔德 | 自行计算 |
| Elder Ray | — | 埃尔德 | 自行计算 |
| TD Setup/TD Countdown | — | 德马克 | 自行实现 |
| Ichimoku | — | 细田(阶段三) | 自行实现 |
| Alligator/Fractal/AO/AC | — | B.威廉姆斯(阶段三) | 自行实现 |

- **推荐方案**：优先使用 `pandas-ta` 库（覆盖80%指标），TD序列、一目均衡等需手写

#### `fundamental_data.py` — 基本面数据引擎
- **数据源**：
  - 美股：yfinance（info接口获取PE/PB/市值/营收/利润）+ financialmodelingprep（财报）
  - A股：akshare（stock_financial_abstract_ths 获取财务摘要、stock_a_lg_indicator 获取估值）
  - 港股：yfinance + akshare（stock_hk_financial_indicator_ths）
- **输出数据**：
  - 估值指标：PE(TTM)、PB、PS、EV/EBITDA、股息率
  - 财务指标：营收/净利润增长率（3年/5年CAGR）、ROE、毛利率、净利率、资产负债率
  - 行业数据：同行业可比公司对比、行业PE中位数
  - 机构持仓：主要机构持仓变化（美股）、北向资金（A股）

#### `cache.py` — 缓存机制
- 二级缓存：内存（LRU，100条） + 本地文件（JSON/pickle，TTL 1小时）
- 缓存键：`{symbol}_{market}_{interval}_{period}_{date}`
- 数据引擎调用时先查缓存，命中直接返回
- 基本面数据独立缓存（TTL 24小时，财报数据不频繁变动）

### 3.2 大师分析管道 (`masters/`)

#### `base_master.py` — 大师基类
```python
class BaseMaster:
    def __init__(self, name: str, stage: int, llm_client):
        self.name = name
        self.stage = stage          # 1/2/3
        self.perspective_file: str  # 对应 skill_references/ 下的框架文件
    
    def analyze(self, context: dict) -> MasterOpinion:
        """核心方法：读取数据 + 加载框架 → 调用LLM → 返回结构化观点"""
        pass
```

**`MasterOpinion` 数据结构**（统一接口，各阶段扩展）：
```python
@dataclass
class MasterOpinion:
    master_name: str           # 大师名称
    stage: int                 # 所属阶段（1/2/3）
    stance: str                # "bullish" / "bearish" / "neutral" / "avoid"
    confidence: float          # 0~1 置信度
    reasoning: str             # 分析推理
    key_levels: list[float]    # 关键价位（阶段二/三使用）
    signals: list[str]         # 信号标签
    risk_warning: str          # 风险提示
    # 阶段一扩展字段
    valuation: Optional[dict]  # 估值分析（仅阶段一）
    # 阶段三扩展字段
    signal_strength: Optional[int]   # 信号强度0~100（仅阶段三）
    entry_target: Optional[float]    # 入场/目标/止损（仅阶段三）
```

#### 阶段一：投资大师（定性辩论 — 14人）

**数据需求**：基本面数据（fundamental_data.py）而非OHLCV

**七步辩论流程**（参考已运行的FUTU富途报告模式）：
1. 数据校准：所有大师读取同一套基本面数据
2. 独立估值：每位大师基于自身框架给出估值判断
   - ⚠️ **铁律 §11.1**：观点陈述必须完整呈现，包含立场+依据+数据+风险提示，禁止用一句话替代
3. 阵营划分：按看多/中立/回避自动分组
4. 辩论交锋：选择关键分歧点进行辩论，每个话题至少2轮实质性交锋
   - ⚠️ **铁律 §11.1**：交锋必须展现跨流派碰撞、大师个性风格，禁止压缩成"XX和YY进行了讨论"
5. 投票统计：看多票数 / 中立票数 / 回避票数
6. 概率加权（可选）
7. 最终判断：提取共识 + 保留分歧

**大师分组**：
- **价值学派**（巴菲特/芒格/格雷厄姆）：安全边际、护城河、内在价值折价
- **成长学派**（林奇/伍德/张磊）：增长潜力、颠覆性创新、长期结构性价值
- **宏观学派**（达利欧/索罗斯）：宏观周期、反身性、概率分布
- **逆向/实用学派**（马克斯/段永平/李录/冯柳/邱国鹭/林园）：第二层思维、赔率、品牌垄断

#### 阶段二：技术分析大师（趋势/形态/量价 — 12人）

**数据需求**：OHLCV + 预计算技术指标

**12位大师覆盖**：
- **趋势派**：道氏（主要/次要趋势）、艾略特（波浪计数）、葛兰碧（量价八法则）、阿佩尔（MACD趋势）
- **形态派**：尼森（K线形态识别）、威科夫（量价关系/吸筹派发）
- **动量派**：威尔德（RSI/DMI/ADX/ATR）、莱恩（KDJ）、威廉姆斯（W%R）
- **综合派**：埃尔德（三重滤网）、德马克（TD序列/TD计数）、ARBR团队（人气意愿指标）

**提示词要求**：按决策流程分析趋势方向、识别形态、输出关键价位。

#### 阶段三：技术指标大师（纯数字信号 — 11人）

**数据需求**：OHLCV + 预计算技术指标（定制化数据包）

**11位大师及覆盖指标**：
| 大师 | 覆盖指标 | 输出类型 |
|------|----------|----------|
| Gerald Appel | MACD | 金叉/死叉价位、目标位 |
| John Bollinger | 布林带 | 上/中/下轨、突破/回归 |
| Joseph Granville | MA法则+OBV | 均线支撑/阻力、OBV背离 |
| Goichi Hosoda | 一目均衡表 | 云层支撑/阻力、转换线/基线交叉 |
| J. Welles Wilder | RSI/DMI/ADX/ATR/PSAR | RSI超买超卖、ADX趋势强度、ATR止损位 |
| George Lane | Stochastic/KDJ | %K/%D交叉、超买超卖区 |
| Donald Lambert | CCI | CCI超买超卖、趋势通道突破 |
| Larry Williams | Williams %R | %R超买超卖、背离信号 |
| Marc Chaikin | Chaikin Money Flow | CMF正负、资金流入流出 |
| Alexander Elder | 三重滤网系统 | 多时间框架信号、趋势确认位 |
| Bill Williams | 混沌操作法 | 鳄鱼线、分形、AO/AC动量 |

**执行流程**（参考design文档）：
1. 数据准备：11位大师并行获取定制化数据包
2. 独立输出：每人输出信号方向+强度+关键价位
   - ⚠️ **铁律 §11.1**：每位大师的信号报告必须包含完整的指标状态描述和推理，禁止仅输出方向标签
3. 冲突检测：标记看涨/看跌对立对
4. 定向辩论：仅冲突对参与，每个冲突话题至少2轮实质性交锋
   - ⚠️ **铁律 §11.1**：交锋必须展现各大师指标框架推理和个性风格，禁止压缩成一句话总结
5. 投票统计：加权净方向 + 分歧度计算
6. 操作建议：基于共识给出入场/止损/目标位

#### 阶段三提示词模板（与阶段一/二不同的独立模板）
```
你是一位技术指标大师 [{大师姓名}]，请基于以下框架和数据输出技术信号。

## 你的指标框架
{从 skill_references 加载}

## 当前数据
股票：{symbol}
当前价格：{price}

指标数值：
- [指标1]：[数值/状态]

## 输出要求（严格JSON）
{
  "signal_direction": "bullish" | "bearish" | "neutral",
  "signal_strength": 0-100,
  "support_level": 支撑位,
  "breakout_level": 突破位,
  "target_high": 目标价上限,
  "target_low": 目标价下限,
  "stop_loss": 止损位,
  "indicator_status": "指标状态描述",
  "market_condition": "当前市场环境说明"
}
```

#### LLM 配置
- 优先使用 OpenAI 兼容 API（支持 deepseek/qwen/gpt-4o 等任何模型）
- 在 `config.py` 中配置 `LLM_API_BASE`、`LLM_API_KEY`、`LLM_MODEL`
- 阶段一14人 + 阶段二12人 + 阶段三11人，分阶段串行，同阶段内并行调用（`asyncio.gather`）
- 超时控制：阶段一每人大师60秒，阶段二每人30秒，阶段三每人15秒

### 3.3 辩论协调器 (`debate_orchestrator/`)

#### `orchestrator.py` — 主协调器
```
输入：symbol + market
流程：
  1. 调用 data_engine 拉取技术数据 + 基本面数据
  2. 调用 stage1_debate 执行14人定性辩论
  3. 调用 stage2_analysis 执行12人技术分析
  4. 调用 stage3_signals 执行11人技术信号 + 冲突辩论 + 投票
  5. 调用 cross_stage_conflict 检测跨阶段冲突（如：基本面看多 vs 技术面看空）
  6. 调用 aggregator 生成综合建议
输出：DebateResult
```

**`DebateResult` 数据结构**：
```python
@dataclass
class DebateResult:
    symbol: str; market: str; current_price: float; analysis_date: str
    stage1_result: Stage1DebateResult    # 阶段一结果
    stage2_result: Stage2AnalysisResult  # 阶段二结果
    stage3_result: Stage3SignalResult    # 阶段三结果
    cross_stage_conflicts: list[Conflict]
    overall_consensus: str
    overall_confidence: float
    action_recommendation: str
    key_risk_factors: list[str]
```

#### `stage1_debate.py` — 阶段一：14人定性辩论
- 执行七步辩论流程（数据校准→独立估值→阵营划分→辩论交锋→投票→概率加权→最终判断）
- 输出：看多/中立/回避阵营结果 + 关键共识 + 保留分歧

#### `stage2_analysis.py` — 阶段二：12人技术分析
- 并行调用12位大师产出 MasterOpinion
- 整合趋势/形态/量价分析结果

#### `stage3_signals.py` — 阶段三：11人技术信号
- 数据分发→独立输出→冲突检测→定向辩论→投票统计→操作建议
- 输出信号矩阵 + 投票统计 + 内部辩论记录

#### `cross_stage_conflict.py` — 跨阶段冲突检测
- 检测阶段一（基本面）与阶段二/三（技术面）的矛盾
- 例如：价值大师看多（低估）但技术指标看空（超买回调）
- 标注为"基本面-技术面分歧"，在最终报告中独立呈现

#### `conflict_detector.py` — 冲突检测（各阶段通用）
- 检测同阶段内观点对立（阶段二/三使用）
- 检测多空阵营对峙
- 势均力敌时标注为高风险分歧

#### `aggregator.py` — 三阶段聚合
- 阶段一：定性结论（价值判断）权重60%
- 阶段二：趋势确认 权重20%
- 阶段三：信号时机 权重20%
- 加权得出最终操作建议

### 3.4 报告生成器 (`report_generator/`)

#### `markdown_report.py` — Markdown 圆桌纪要
**输出模板结构**：
```markdown
# 技术分析圆桌会议纪要 — {symbol} {date}

## 基本信息
- 股票：{name}（{symbol}）
- 当前价格：{price}
- 分析日期：{date}

## 投票结果
| 观点 | 票数 | 大师 |
|------|------|------|
| 🟢 看多 | {n} | 道、威科夫、艾略特... |
| 🔴 看空 | {n} | 德马克、威廉姆斯... |
| ⚪ 中性 | {n} | 尼森、ARBR |

## 综合建议：{bullish/bearish/divided}
{操作建议} | 综合置信度：{score}%

## 12位大师详细分析
[每位大师一个折叠块]
### {大师名} — {看多/看空/中性} | 置信度 {n}%
{reasoning}
关键价位：支撑 {s} / 阻力 {r}
信号：{signal_list}
风险：{risk_warning}

## 关键分歧点
1. {冲突1描述}
2. {冲突2描述}

## 风险提示
- {风险1}
- {风险2}
```

#### `chart_renderer.py` — 技术图表
- 使用 `mplfinance` 绘制日K线图
- 叠加 MA5/10/20/50/200
- 标注关键价位（支撑/阻力水平线）
- 图例标注各大师的看多/看空立场（用不同颜色标记）
- 可选子图：成交量 + MACD + RSI

#### `html_report.py` — HTML 可视化报告
- 嵌入图表（base64 编码的图片）
- Bootstrap 风格布局
- 交互式大师观点卡片（hover 展开详情）
- 投票结果用饼图/柱状图展示

### 3.5 Web 界面 (`web_app/`)

#### `app.py` — Flask 应用
- 路由：`GET /` — 主页（输入框）
- 路由：`POST /analyze` — 触发分析，返回报告页面
- 路由：`GET /report/{id}` — 查看历史报告
- 支持异步分析（SSE 或 WebSocket 推送分析进度）

#### 前端界面
- 输入区域：股票代码输入框 + 市场选择下拉（A股/美股/港股）+ 分析按钮
- 加载状态：显示"正在拉取数据..." → "12位大师分析中..." 进度条
- 结果展示：嵌入生成的 HTML 报告

## 四、数据流示意

```
run.py 启动
  → config.py 读取配置
  → data_engine/cache.py 检查缓存
  → [并行] data_engine/fetcher.py 拉取OHLCV（如缓存未命中）
  → [并行] data_engine/fundamental_data.py 拉取基本面数据（如缓存未命中）
  → data_engine/technical_indicators.py 预计算全部技术指标
  → debate_orchestrator/orchestrator.py 三阶段编排:
      → 阶段一：[串行先执行] stage1_debate.py
          → 并行调用 masters/stage1/*.py（14人，每人调用LLM）
          → 七步辩论流程
      → 阶段二：stage2_analysis.py
          → 并行调用 masters/stage2/*.py（12人，每人调用LLM）
      → 阶段三：stage3_signals.py
          → 并行调用 masters/stage3/*.py（11人，每人调用LLM + 预计算）
          → 冲突检测 + 定向辩论 + 投票统计
      → cross_stage_conflict.py 跨阶段冲突检测
      → aggregator.py 三阶段加权聚合
  → report_generator 生成:
      → markdown_report.py → .md 文件
      → chart_renderer.py → .png 图表
      → html_report.py → .html 报告
  → 输出到 examples/ 目录
```

## 五、依赖清单 (`requirements.txt`)

```
# 数据获取
yfinance>=0.2.40
akshare>=1.14.0

# 基本面数据（可选，增强功能）
financialmodelingprep>=0.0.1  # 美股财报数据（需API Key）

# 技术指标计算
pandas-ta>=0.3.14b
TA-Lib>=0.4.28           # 备选（需要先安装 C 库）

# 数据处理
pandas>=2.2.0
numpy>=1.26.0

# LLM 调用
openai>=1.30.0           # 兼容 openai / deepseek / qwen 等

# 异步
aiohttp>=3.9.0

# 可视化
mplfinance>=0.12.10b0
matplotlib>=3.8.0

# Web 框架
flask>=3.0.0
markdown>=3.5.0

# 工具
python-dotenv>=1.0.0
pydantic>=2.5.0
```

## 六、配置文件 (`config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

# LLM 配置
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

# 数据源配置
YFINANCE_ENABLED = True
AKSHARE_ENABLED = True
FMP_API_KEY = os.getenv("FMP_API_KEY", "")  # financialmodelingprep API key

# 缓存配置
CACHE_DIR = "./cache"
CACHE_TTL_HOURS = 1
FUNDAMENTAL_CACHE_TTL_HOURS = 24  # 基本面数据缓存更久
MEMORY_CACHE_SIZE = 100

# 输出配置
OUTPUT_DIR = "./examples"
CHART_STYLE = "yahoo"  # mplfinance 样式

# 数据配置
DEFAULT_PERIOD = "2y"   # 默认拉取2年数据
DEFAULT_INTERVAL = "1d"

# 大师配置
MASTER_REFERENCE_DIR = "./masters/skill_references"
STAGE1_COUNT = 14
STAGE2_COUNT = 12
STAGE3_COUNT = 11

# 超时控制
STAGE1_TIMEOUT_SECONDS = 60   # 阶段一每人大师60秒
STAGE2_TIMEOUT_SECONDS = 30   # 阶段二每人30秒
STAGE3_TIMEOUT_SECONDS = 15   # 阶段三每人15秒
TOTAL_TIMEOUT_SECONDS = 300   # 总超时5分钟

# 权重配置
STAGE1_WEIGHT = 0.6   # 阶段一（基本面）权重60%
STAGE2_WEIGHT = 0.2   # 阶段二（趋势确认）权重20%
STAGE3_WEIGHT = 0.2   # 阶段三（信号时机）权重20%
```

## 七、主入口 (`run.py`)

```python
"""
用法：
  python run.py --symbol AAPL --market US
  python run.py --symbol 000001 --market CN
  python run.py --symbol 0700.HK --market HK
  python run.py --symbol AAPL --market US --web  # 启动 Web 界面
"""
```

**命令行参数**：
- `--symbol`：股票代码（必填）
- `--market`：市场（US/CN/HK，默认US）
- `--period`：数据周期（默认2y）
- `--web`：启动 Web 界面而非命令行
- `--output`：报告输出目录（默认 ./examples）

## 八、实现顺序（优先级）

| 优先级 | 模块 | 预计工时 | 说明 |
|--------|------|---------|------|
| P0 | `data_engine/fetcher.py` | 0.5天 | 先让系统能拉到真实数据 |
| P0 | `data_engine/cache.py` | 0.25天 | 避免重复调API被限流 |
| P0 | `config.py` | 0.25天 | 全局配置骨架 |
| P1 | `data_engine/technical_indicators.py` | 1.5天 | 预计算所有技术指标（含阶段三新增） |
| P1 | `data_engine/fundamental_data.py` | 1天 | 基本面数据引擎（支持阶段一） |
| P1 | `masters/base_master.py` | 0.5天 | 大师基类 + LLM调用逻辑 |
| P2 | `masters/stage1/*.py`（14个） | 2天 | 阶段一投资大师（框架加载+prompt+解析） |
| P2 | `debate_orchestrator/stage1_debate.py` | 1天 | 七步辩论流程 |
| P3 | `masters/stage2/*.py`（12个） | 1.5天 | 阶段二技术分析大师 |
| P3 | `masters/stage3/*.py`（11个） | 2天 | 阶段三技术指标大师 + signal_masters Skill创建 |
| P4 | `debate_orchestrator/stage2_analysis.py` | 0.5天 | 阶段二编排 |
| P4 | `debate_orchestrator/stage3_signals.py` | 1天 | 阶段三编排 |
| P4 | `debate_orchestrator/cross_stage_conflict.py` | 0.5天 | 跨阶段冲突检测 |
| P4 | `debate_orchestrator/aggregator.py` | 0.5天 | 三阶段加权聚合 |
| P5 | `report_generator/` | 1.5天 | Markdown+图表+HTML |
| P6 | `web_app/` | 0.5天 | Flask界面 |
| P6 | `tests/` | 1天 | 单元测试（三阶段独立测试） |
| P7 | `README.md` + Git整理 | 0.5天 | 开源准备 |

**总计：约16个工作日（含阶段三11个signal_masters Skill创建）**

## 九、关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 架构模式 | 三阶段串行，阶段内并行 | 阶段一（定性结论）为阶段二/三提供上下文，阶段二/三提供技术确认和时间节点 |
| LLM调用方式 | 统一OpenAI兼容API | deepseek/qwen/gpt-4o 任意切换 |
| 大师分析方式 | 每人独立LLM调用（阶段内并行） | 避免上下文污染，保持观点独立性 |
| 数据双轨制 | 技术数据轨 + 基本面数据轨 | 阶段一需要财报/估值，阶段二/三需要OHLCV |
| 指标计算 | 预计算（一次性算好） | 避免26位（阶段二+三）大师重复计算相同指标 |
| 缓存策略 | 文件+内存二级缓存 + 分别TTL | 技术数据1小时，基本面数据24小时 |
| 报告格式 | Markdown + HTML | Markdown给Git展示，HTML给Web交互 |
| 数据源 | yfinance + akshare + FMP 多源 | 覆盖全球市场 + 基本面，免费为主 |
| 跨阶段权重 | 阶段一60% + 阶段二20% + 阶段三20% | 基本面定性判断权重最高，技术面提供确认和时机 |
| Skill文件管理 | 按阶段分目录 + 统一命名规则 | 31个文件的维护需要明确组织结构 |
| 已生成的Skill文件 | 26个已就绪（14+12），11个待创建 | 阶段三signal_masters需要新蒸馏11个 |

## 十、预期震撼效果

1. **31位大师三阶段分析**：阶段一14人定性辩论（含七步辩论流程），阶段二12人技术分析，阶段三11人纯数字信号输出 + 内部辩论
2. **真实运行**：输入任何股票代码立即产出分析，双轨数据（基本面+技术面）
3. **阶段一：14位投资大师定性辩论**：巴菲特/芒格/格雷厄姆/林奇/马克斯/伍德/索罗斯/达利欧/段永平/张磊/李录/冯柳/邱国鹭/林园
4. **阶段二：12位技术分析大师**：道/威科夫/艾略特/尼森/威尔德/阿佩尔/葛兰碧/德马克/莱恩/威廉姆斯/埃尔德/ARBR
5. **阶段三：11位技术指标大师**：Appel/Bollinger/Granville/Hosoda/Wilder/Lane/Lambert/L.Williams/Chaikin/Elder/B.Williams，带信号强度、关键价位、内部辩论和投票统计
6. **可视化**：K线图叠加支撑/阻力/目标/止损位，标注多空阵营
7. **跨阶段冲突检测**：当基本面看多但技术面看空时，标注"You are trading against Graham"等高质量风险提示
8. **任务优先级总结**：
   - **已完成**：26个Skill文件（14投资大师 + 12技术分析大师）、行业研究Skill、SPEC规格书
   - **待完成**：11个阶段三signal_masters Skill蒸馏、Python代码实现（约16个工作日）
9. **开源友好**：`.env` 管理密钥，README 有完整使用指南 + 截图
10. **可扩展**：新增一位大师只需添加 `masters/stageN/new_master.py` + perspective 文件

---

## 十一、输出质量铁律

### 11.1 辩论完整性（最高优先级）

**规则**：任何阶段的圆桌辩论报告，必须包含**完整的辩论环节**，禁止省略或过度简略以下内容：

1. **观点提出**：每位大师的初始立场陈述必须完整呈现，包含其核心推理逻辑、依据的数据和估值框架。不得仅用"XX看多"一句话替代。
2. **跨流派交锋**：辩论必须有实质性的来回交锋对话，展现不同学派之间的真实碰撞。每个辩论话题至少2轮交锋，交锋中必须体现大师的个性风格和推理方式。

**反面案例（禁止）**：
- 只写"巴菲特看多，格雷厄姆谨慎"而不展示具体推理
- 辩论环节压缩成"XX和YY就估值问题进行了讨论"
- 跳过观点陈述直接跳到投票结果

**正面标准**：
- 每位大师的观点陈述包含：立场 + 核心依据 + 数据支撑 + 风险提示
- 辩论交锋包含：挑战者质疑 → 被挑战者回应 → 反质疑 → 最终立场（可保留分歧）
- 辩论对话中展现大师的独特语言风格和思维习惯

**来源**：本条铁律来自 2026-05-23 实际运行反馈——用户指出"观点提出和辩论环节为什么全部省略了"，此后确认为不可妥协的输出底线。