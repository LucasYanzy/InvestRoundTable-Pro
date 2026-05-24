# 阶段三：技术指标信号层实现计划

## 项目概述

基于设计文档《2026-05-23-technical-signal-roundtable-design.md》，实现圆桌辩论系统的第三阶段——技术指标信号层。该层为纯数字输出层，11位技术指标创始人独立输出信号方向+关键价位，仅在信号冲突时触发内部辩论。

## 项目范围

### 包含
1. 11位技术指标创始人的Skill文件（按人物拆，每个Skill包含其所有指标的综合判断）
2. 阶段三编排器（负责数据准备、冲突检测、辩论触发、投票统计）
3. 数据调度编排Skill的扩展（为11位大师提供定制化数据包）
4. 最终报告格式扩展（在现有编排器输出末尾增加阶段三章节）

### 不包含
1. 数据获取基础设施（复用现有yfinance/akshare数据调度编排Skill）
2. 阶段一/阶段二的修改（仅新增阶段三）
3. 前端界面（仅后端Skill实现）

## 实现步骤

### 阶段一：基础设施准备（1天）

#### 1.1 数据调度编排Skill扩展
- 扩展现有数据调度编排Skill，支持11位大师的预计算数据包
- 实现数据缓存机制（1小时TTL）
- 为每位大师生成定制化数据包（见设计文档"数据分发"部分）

#### 1.2 技术指标计算库
- 创建 `technical_indicators.py` 工具库，包含：
  ```python
  # 标准指标计算
  def calculate_macd(ohlcv_df, fast=12, slow=26, signal=9)
  def calculate_rsi(ohlcv_df, period=14)
  def calculate_bollinger_bands(ohlcv_df, period=20, std_dev=2)
  def calculate_stochastic(ohlcv_df, k_period=14, d_period=3)
  def calculate_cci(ohlcv_df, period=20)
  def calculate_williams_r(ohlcv_df, period=14)
  def calculate_atr(ohlcv_df, period=14)
  def calculate_psar(ohlcv_df, af=0.02, max_af=0.2)
  def calculate_obv(ohlcv_df)
  def calculate_cmf(ohlcv_df, period=20)
  
  # 信号强度计算辅助
  def calculate_signal_strength(indicator_name, indicator_value, threshold_config)
  ```

#### 1.3 目录结构准备
```
skills/investment-masters/
├── roundtable/              # 阶段一（14人，已有）
├── tech-roundtable/         # 阶段二（6人，已有）
├── signal-roundtable/       # 阶段三（11人，新增）
│   ├── INDEX.md            # 阶段三索引
│   ├── gerald-appel-perspective-SKILL.md
│   ├── john-bollinger-perspective-SKILL.md
│   ├── joseph-granville-perspective-SKILL.md
│   ├── goichi-hosoda-perspective-SKILL.md
│   ├── welles-wilder-perspective-SKILL.md
│   ├── george-lane-perspective-SKILL.md
│   ├── donald-lambert-perspective-SKILL.md
│   ├── larry-williams-perspective-SKILL.md
│   ├── marc-chaikin-perspective-SKILL.md
│   ├── alexander-elder-perspective-SKILL.md
│   └── bill-williams-perspective-SKILL.md
└── signal-orchestrator-SKILL.md  # 阶段三编排器（新增）
```

### 阶段二：技术指标创始人Skill创建（3天）

#### 2.1 Skill模板设计
每个Skill遵循12段模板结构（与投资大师Skill保持一致）：
```
# [蒸馏入口] [大师姓名] · 技术指标信号

## 大师档案
## 投资哲学底色
## 心智模型与决策启发式
## 理性估值边界
## 核心理论框架
## 决策流程
## 圆桌辩论角色
## 与其他大师互动关系
## 辩论输出模板
## 数据纪律
## 口头禅与辩论战术动作
## 版本历史
```

#### 2.2 关键实现要点
- **输出模板**：必须严格遵循设计文档中的标准模板（信号方向+信号强度+关键价位+指标状态+适用条件）
- **信号强度计算**：每个Skill内部实现自己的强度计算逻辑（基于指标数值与阈值关系）
- **关键价位计算**：基于指标框架计算支撑位、突破位、目标价、止损位
- **辩论准备**：预置与其他大师的潜在冲突点和反驳逻辑

#### 2.3 创建顺序（按流派分组）
1. **趋势派**：Appel (MACD) → Bollinger (布林带) → Granville (MA+OBV) → Hosoda (一目均衡)
2. **动量派**：Wilder (RSI/DMI/ADX/ATR/PSAR) → Lane (Stochastic/KDJ) → Lambert (CCI) → L. Williams (W%R)
3. **成交量派**：Chaikin (CMF)
4. **综合派**：Elder (三重滤网) → B. Williams (混沌操作法)

### 阶段三：编排器实现（2天）

#### 3.1 signal-orchestrator-SKILL.md 设计
编排器负责：
```
步骤1：数据准备
  - 调用数据调度编排Skill获取OHLCV数据
  - 预计算标准指标基础数据

步骤2：独立输出（11人并行）
  - 加载11位大师Skill
  - 为每位大师分发定制化数据包
  - 收集11份信号报告

步骤3：冲突检测
  - 扫描信号方向
  - 标记相反信号的大师对
  - 如无冲突，跳过辩论步骤

步骤4：定向辩论（仅冲突对参与）
  - 触发1-2轮辩论
  - 焦点："为什么当前市场环境下你的框架更可靠？"
  - 记录辩论内容

步骤5：投票统计
  - 计算加权净方向 = (Σ看涨强度 - Σ看跌强度) / (Σ总强度)
  - 计算分歧度 = 1 - |净方向|

步骤6：最终输出
  - 信号矩阵表格
  - 辩论记录（如有）
  - 投票统计
  - 操作建议
```

#### 3.2 与现有编排器的集成
- 修改 `roundtable-orchestrator-SKILL.md`，在阶段二之后增加阶段三调用
- 最终报告结构扩展：
  ```
  ## 综合报告
  
  ### 定性结论（阶段一）
  ### 技术审计（阶段二）
  ### 投资评级（三合一机制）
  ### 技术信号（阶段三）  ← 新增
  
  ## 操作指引（由阶段三信号充实）
  ## 跟踪节点
  ```

### 阶段四：测试与验证（1天）

#### 4.1 测试用例
1. **单标的全流程测试**：选择AAPL（美股）、贵州茅台（A股）测试完整三阶段流程
2. **冲突场景测试**：模拟MACD看涨 vs KDJ看跌的冲突场景，验证辩论触发
3. **数据边界测试**：测试数据缺失、数据异常时的降级处理
4. **性能测试**：11位大师并行计算的响应时间

#### 4.2 质量门验证
对照设计文档中的质量门：
- [ ] 11位大师都输出了信号方向+数值参数
- [ ] 信号冲突时触发了辩论
- [ ] 输出包含信号矩阵+投票统计+操作建议三部分
- [ ] 操作建议基于共识（而非单一大师）
- [ ] 信号强度明确定义

## 技术细节

### 数据接口
```python
# 数据调度编排Skill返回的数据结构
{
  "symbol": "AAPL",
  "ohlcv": {
    "date": ["2026-05-20", "2026-05-21", ...],
    "open": [150.0, 152.0, ...],
    "high": [155.0, 154.0, ...],
    "low": [149.0, 151.0, ...],
    "close": [153.0, 152.5, ...],
    "volume": [1000000, 1200000, ...]
  },
  "precomputed": {
    "macd": {"diff": [...], "dea": [...], "histogram": [...]},
    "rsi": [...],
    "bollinger": {"upper": [...], "middle": [...], "lower": [...], "width": [...]}
    # ... 其他预计算指标
  }
}
```

### 信号强度计算示例（Appel - MACD）
```python
def calculate_macd_signal_strength(macd_diff, macd_dea, histogram):
    """
    计算MACD信号强度（0-100）
    规则：
    - 金叉/死叉：基础分60
    - 柱状图斜率：±20
    - DIFF-DEA距离：±20
    """
    strength = 0
    
    # 金叉/死叉判断
    if macd_diff[-1] > macd_dea[-1] and macd_diff[-2] <= macd_dea[-2]:  # 金叉
        strength += 60
    elif macd_diff[-1] < macd_dea[-1] and macd_diff[-2] >= mact_dea[-2]:  # 死叉
        strength += 60
    
    # 柱状图斜率
    if len(histogram) >= 2:
        slope = histogram[-1] - histogram[-2]
        if slope > 0:  # 柱状图上升
            strength += min(20, abs(slope) * 10)
        else:  # 柱状图下降
            strength -= min(20, abs(slope) * 10)
    
    # DIFF-DEA距离
    distance = abs(macd_diff[-1] - macd_dea[-1])
    strength += min(20, distance * 5)
    
    return max(0, min(100, strength))
```

### 辩论触发逻辑
```python
def detect_conflicts(signals):
    """
    signals: dict {master_name: {"direction": "bullish"/"bearish"/"neutral", ...}}
    返回冲突对列表 [(master1, master2), ...]
    """
    bullish_masters = [m for m, s in signals.items() if s["direction"] == "bullish"]
    bearish_masters = [m for m, s in signals.items() if s["direction"] == "bearish"]
    
    conflicts = []
    for bull in bullish_masters:
        for bear in bearish_masters:
            conflicts.append((bull, bear))
    
    # 只选最尖锐的1-2对冲突（按信号强度差排序）
    if len(conflicts) > 2:
        conflicts.sort(key=lambda pair: abs(
            signals[pair[0]]["strength"] - signals[pair[1]]["strength"]
        ), reverse=True)
        conflicts = conflicts[:2]
    
    return conflicts
```

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 数据源不稳定 | 阶段三无法执行 | 实现数据源降级（yfinance失败→akshare；都失败→使用缓存数据） |
| 11位大师并行计算超时 | 响应时间过长 | 设置超时限制（单大师30秒），超时则使用默认中性信号 |
| 信号强度计算不一致 | 投票统计失真 | 为每个Skill提供强度计算参考实现，确保逻辑一致 |
| 与现有编排器集成冲突 | 流程中断 | 先独立测试阶段三，再集成到完整流程 |

## 交付物

1. **11个技术指标创始人Skill文件**（signal-roundtable/目录下）
2. **阶段三编排器**（signal-orchestrator-SKILL.md）
3. **数据调度编排Skill扩展**（复用现有，仅扩展）
4. **技术指标计算库**（technical_indicators.py）
5. **更新后的完整编排器**（roundtable-orchestrator-SKILL.md v1.2，集成阶段三）
6. **测试报告**（包含质量门验证结果）

## 时间估算

| 阶段 | 任务 | 工时 | 依赖 |
|------|------|:---:|------|
| 1 | 基础设施准备 | 8h | - |
| 2 | 11个Skill创建 | 24h | 阶段1 |
| 3 | 编排器实现 | 16h | 阶段2 |
| 4 | 测试与验证 | 8h | 阶段3 |
| **总计** | | **56h** | |

## 下一步

1. 确认实现计划
2. 开始阶段一：基础设施准备
3. 按顺序创建11个技术指标创始人Skill
4. 实现编排器并集成到现有系统
5. 全面测试

---
*计划版本：v1.0 | 创建日期：2026-05-23 | 基于设计文档：2026-05-23-technical-signal-roundtable-design.md*