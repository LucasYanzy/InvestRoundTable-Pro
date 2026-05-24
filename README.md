<div align="center">

# 🏛️ Investment Masters Roundtable

### 31位投资大师三阶段圆桌辩论系统

**14 位价值投资大师 × 12 位技术分析大师 × 11 位量化信号大师**
**三阶段分析你的股票 — 产出圆桌辩论纪要 + 技术图表 + 综合投资建议**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![LLM: OpenAI Compatible](https://img.shields.io/badge/LLM-OpenAI%20Compatible-412991.svg?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/docs/api-reference)
[![Data: yfinance + akshare](https://img.shields.io/badge/data-yfinance%20%2B%20akshare-orange.svg?style=flat-square)](https://github.com/ranaroussi/yfinance)

[快速开始](#-快速开始) · [项目结构](#-项目结构) · [大师名录](#-37位大师三阶段) · [技术栈](#-技术栈) · [配置说明](#-配置说明)

</div>

---

## ✨ 核心亮点

| 特性 | 说明 |
|------|------|
| 🏛️ **三阶段分析架构** | 基本面定性辩论 → 技术趋势判断 → 量化信号投票，层层递进 |
| ⚔️ **真实辩论交锋** | 多空阵营代表进行 2 轮 LLM 驱动的对抗辩论，不是简单汇总 |
| ⚠️ **跨阶段冲突检测** | 基本面 vs 技术面矛盾时独立标注："You are trading against Graham" |
| 📊 **信号矩阵投票** | 11 位指标大师独立出信号 → 加权投票 → 净方向得分 |
| 📈 **一键可视化** | K 线图叠加均线/布林/RSI/MACD + 支撑阻力标注 |
| 🌐 **多市场支持** | 美股 / A 股 / 港股，yfinance + akshare 双源覆盖 |

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/yourusername/investment-masters-roundtable.git
cd investment-masters-roundtable

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 4. 运行分析
python run.py --symbol AAPL --market US       # 美股苹果
python run.py --symbol 000001 --market CN     # A股平安银行
python run.py --symbol 0700.HK --market HK    # 港股腾讯
python run.py --web                            # 启动 Web 界面
```

## 📁 项目结构

```
investment-masters-roundtable/
│
├── run.py                        # CLI 入口 + Web 启动器
├── config.py                     # 全局配置（环境变量驱动）
│
├── data_engine/                  # 数据层
│   ├── fetcher.py                #   OHLCV 行情拉取（yfinance + akshare）
│   ├── fundamental_data.py       #   基本面数据（估值/财务/行业）
│   ├── technical_indicators.py   #   20+ 技术指标预计算
│   ├── cache.py                  #   二级缓存（内存 LRU + 文件 pickle）
│   └── schema.py                 #   统一数据结构定义
│
├── masters/                      # 37 位大师分析层
│   ├── base_master.py            #   大师基类 + LLM 调用 + MasterOpinion
│   ├── registry.py               #   37 位大师注册表（纯数据）
│   ├── investment_master.py      #   阶段一: InvestmentMaster（14 位）
│   ├── technical_master.py       #   阶段二: TechnicalMaster（12 位）
│   ├── signal_master.py          #   阶段三: SignalMaster（11 位）
│   └── skill_references/         #   大师投资框架文件（.md）
│       ├── investment_masters/   #     14 份价值投资框架
│       ├── technical_masters/    #     12 份技术分析框架
│       └── signal_masters/       #     11 份量化信号框架
│
├── debate_orchestrator/          # 辩论协调层
│   ├── orchestrator.py           #   主编排器（三阶段串行调度）
│   ├── stage1_debate.py          #   阶段一: 七步辩论流程
│   ├── stage2_analysis.py        #   阶段二: 并行趋势分析
│   ├── stage3_signals.py         #   阶段三: 信号矩阵 + 内部辩论
│   ├── conflict_detector.py      #   阶段内冲突检测
│   ├── cross_stage_conflict.py   #   跨阶段冲突检测
│   ├── confidence_scorer.py      #   综合置信度评分
│   └── aggregator.py             #   三阶段加权聚合（60/20/20）
│
├── report_generator/             # 报告生成层
│   ├── markdown_report.py        #   Markdown 圆桌纪要
│   ├── html_report.py            #   暗色主题 HTML 报告
│   └── chart_renderer.py         #   mplfinance 技术图表
│
├── web_app/                      # Web 界面（可选）
│   ├── app.py                    #   Flask 应用
│   └── templates/index.html      #   暗色主题前端
│
├── tests/                        # 测试
│   └── test_smoke.py             #   冒烟测试（导入 + 工厂 + hack 检测）
│
└── docs/                         # 设计文档
```

## 📊 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    用户输入: AAPL + US                       │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  数据引擎                                                    │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  OHLCV   │  │  基本面数据   │  │  20+ 技术指标预计算    │  │
│  │ yfinance  │  │  PE/PB/ROE   │  │  MA/MACD/RSI/KDJ/... │  │
│  │ + akshare │  │  + 行业/估值  │  │  + Elder/Ichimoku/BW │  │
│  └──────────┘  └──────────────┘  └───────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段一: 14 位投资大师定性辩论                                │
│  巴菲特·芒格·格雷厄姆·林奇·马克斯·伍德·索罗斯·达利欧           │
│  段永平·张磊·李录·冯柳·邱国鹭·林园                            │
│  → 七步流程: 独立估值 → 阵营划分 → 2轮辩论 → 投票 → 共识     │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段二: 12 位技术大师趋势/形态/量价分析                      │
│  道·威科夫·艾略特·尼森·威尔德·阿佩尔·葛兰碧·德马克·莱恩·...   │
│  → 并行分析 → 共识支撑/阻力中位数                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段三: 11 位指标大师纯数字信号                              │
│  MACD·布林·MA+OBV·一目均衡·RSI/ADX·KDJ·CCI·W%R·CMF·...     │
│  → 信号矩阵 → 冲突辩论 → 加权投票 → 净方向得分               │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  跨阶段冲突检测 + 60/20/20 加权聚合                           │
│  → ⚠️ "You are trading against Graham" 风险标注              │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  报告输出                                                    │
│  📝 Markdown 圆桌纪要  |  🌐 HTML 可视化报告  |  📈 K线图表  │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 37位大师（三阶段）

<details>
<summary><b>阶段一：14 位投资大师（定性辩论）</b></summary>

| # | 大师 | 学派 | 核心框架 |
|---|------|------|----------|
| 1 | 沃伦·巴菲特 | 价值投资 | 护城河、安全边际、长期持有 |
| 2 | 查理·芒格 | 价值投资 | 多元思维模型、逆向思维 |
| 3 | 本杰明·格雷厄姆 | 价值投资 | 内在价值、市场先生、安全边际 |
| 4 | 彼得·林奇 | 成长投资 | PEG 估值、生活中的投资机会 |
| 5 | 霍华德·马克斯 | 逆向投资 | 第二层思维、周期定位 |
| 6 | 凯瑟琳·伍德 | 颠覆创新 | ARK 颠覆性创新框架 |
| 7 | 乔治·索罗斯 | 宏观对冲 | 反身性理论、趋势交易 |
| 8 | 瑞·达利欧 | 宏观对冲 | 经济机器、债务周期、全天候 |
| 9 | 段永平 | 实用主义 | 本分、商业模式优先 |
| 10 | 张磊 | 成长投资 | 长期结构性价值、动态护城河 |
| 11 | 李录 | 价值投资 | 能力圈、文明 3.0 现代化 |
| 12 | 冯柳 | 逆向投资 | 弱者体系、赔率思维 |
| 13 | 邱国鹭 | 价值投资 | 数月亮不数星星 |
| 14 | 林园 | 消费投资 | 嘴巴股、垄断品牌 |

</details>

<details>
<summary><b>阶段二：12 位技术分析大师（趋势/形态/量价）</b></summary>

| # | 大师 | 核心理论 | 分析重点 |
|---|------|----------|----------|
| 1 | 查尔斯·道 | 道氏理论 | 主要/次要/短期趋势 |
| 2 | 理查德·威科夫 | 威科夫方法 | 量价关系、吸筹/派发 |
| 3 | 拉尔夫·艾略特 | 波浪理论 | 波浪计数、斐波那契 |
| 4 | 史蒂夫·尼森 | 日本蜡烛图 | K 线形态识别 |
| 5 | 威尔德 | RSI/DMI/ADX/ATR | 趋势强度、波动率 |
| 6 | 杰拉尔德·阿佩尔 | MACD | 移动平均收敛发散 |
| 7 | 约瑟夫·葛兰碧 | 量价八法则 | OBV 量价验证 |
| 8 | 托马斯·德马克 | TD 序列 | 精确买卖点 |
| 9 | 乔治·莱恩 | 随机指标 | KDJ 超买超卖 |
| 10 | 拉里·威廉姆斯 | W%R | 极端价位判断 |
| 11 | 亚历山大·埃尔德 | 三重滤网 | 多时间框架分析 |
| 12 | ARBR 团队 | 情绪指标 | 人气意愿、市场情绪 |

</details>

<details>
<summary><b>阶段三：11 位量化信号大师（纯数字信号 + 辩论投票）</b></summary>

| # | 大师 | 覆盖指标 | 输出信号 |
|---|------|----------|----------|
| 1 | Gerald Appel | MACD | 金叉/死叉 + 目标位 |
| 2 | John Bollinger | 布林带 | 上下轨突破/回归 |
| 3 | Joseph Granville | MA + OBV | 均线交叉 + 量价验证 |
| 4 | Goichi Hosoda | 一目均衡表 | 云层支撑/阻力 |
| 5 | J. Welles Wilder | RSI/ADX/ATR/PSAR | 超买超卖 + 趋势强度 |
| 6 | George Lane | KDJ | %K/%D 交叉 |
| 7 | Donald Lambert | CCI | 通道突破 |
| 8 | Larry Williams | W%R | 超买超卖/背离 |
| 9 | Marc Chaikin | CMF | 资金流入流出 |
| 10 | Alexander Elder | 三重滤网 | 多时间框架信号 |
| 11 | Bill Williams | 混沌操作法 | 鳄鱼线/分形/AO/AC |

</details>

## 🔧 技术栈

| 层 | 技术 |
|---|------|
| **数据获取** | `yfinance`（美股/港股）+ `akshare`（A 股） |
| **技术指标** | `pandas-ta` + 纯 pandas/numpy 降级方案 |
| **LLM 集成** | OpenAI 兼容 API（GPT-4o / DeepSeek / Qwen） |
| **并发控制** | `asyncio`（阶段内大师并行，阶段间串行） |
| **可视化** | `mplfinance` + `matplotlib` |
| **Web 界面** | Flask + 暗色主题单页应用 |
| **日志系统** | Python `logging`，支持 `--verbose` 模式 |

## ⚙️ 配置说明

复制 `.env.example` → `.env`：

```ini
# LLM（支持任何 OpenAI 兼容 API）
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o

# 数据
DEFAULT_PERIOD=2y          # 拉取历史长度
FMP_API_KEY=               # 可选: financialmodelingprep

# 阶段权重（总和 = 1.0）
STAGE1_WEIGHT=0.6          # 基本面
STAGE2_WEIGHT=0.2          # 趋势确认
STAGE3_WEIGHT=0.2          # 信号时机
```

## 📈 性能

| 指标 | 数值 |
|------|------|
| **LLM 调用** | 37 次基础 + 最多 6 次辩论 = ~43 次 |
| **分析时间** | 30–120 秒（取决于 LLM 响应速度） |
| **并发** | 阶段内全部大师并行（14 / 12 / 11 并发） |
| **缓存 TTL** | 技术数据 1h，基本面 24h |

## 🤝 贡献

欢迎 Issue 和 PR！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 License

[MIT](LICENSE) © 2026 Lucas Yan

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请 Star 支持！**

</div>