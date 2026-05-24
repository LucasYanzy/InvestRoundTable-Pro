"""37位大师统一注册表

集中管理所有大师的元信息：名称、所属阶段、框架文件路径、关注指标。
所有工厂函数从这里读取数据构建大师实例。
"""

# ──────────────────────────────────────────────────────────────
# 阶段一：14 位投资大师（定性辩论）
# ──────────────────────────────────────────────────────────────

STAGE1_MASTERS = [
    ("沃伦·巴菲特 (Warren Buffett)",       "investment_masters/warren-buffett-perspective.md"),
    ("查理·芒格 (Charlie Munger)",          "investment_masters/charlie-munger-perspective.md"),
    ("本杰明·格雷厄姆 (Benjamin Graham)",   "investment_masters/graham-perspective.md"),
    ("彼得·林奇 (Peter Lynch)",             "investment_masters/peterlynch-perspective.md"),
    ("霍华德·马克斯 (Howard Marks)",        "investment_masters/howard-marks-perspective.md"),
    ("凯瑟琳·伍德 (Cathie Wood)",           "investment_masters/cathie-wood-perspective.md"),
    ("乔治·索罗斯 (George Soros)",          "investment_masters/soros-perspective.md"),
    ("瑞·达利欧 (Ray Dalio)",               "investment_masters/dalio-perspective.md"),
    ("段永平 (Duan Yongping)",              "investment_masters/duanyongping-perspective.md"),
    ("张磊 (Zhang Lei)",                    "investment_masters/zhanglei-perspective.md"),
    ("李录 (Li Lu)",                        "investment_masters/lilu-perspective.md"),
    ("冯柳 (Feng Liu)",                     "investment_masters/fengliu-perspective.md"),
    ("邱国鹭 (Qiu Guolu)",                  "investment_masters/qiuguolu-perspective.md"),
    ("林园 (Lin Yuan)",                     "investment_masters/linyuan-perspective.md"),
]

# ──────────────────────────────────────────────────────────────
# 阶段二：12 位技术分析大师（趋势 / 形态 / 量价）
# ──────────────────────────────────────────────────────────────

STAGE2_MASTERS = [
    ("查尔斯·道 (Charles Dow)",             "technical_masters/charles-dow-perspective.md"),
    ("理查德·威科夫 (Richard Wyckoff)",      "technical_masters/richard-wyckoff-perspective.md"),
    ("拉尔夫·艾略特 (Ralph Elliott)",        "technical_masters/ralph-elliott-perspective.md"),
    ("史蒂夫·尼森 (Steve Nison)",            "technical_masters/steve-nison-perspective.md"),
    ("威尔德 (J. Welles Wilder)",            "technical_masters/welles-wilder-perspective.md"),
    ("杰拉尔德·阿佩尔 (Gerald Appel)",       "technical_masters/gerald-appel-perspective.md"),
    ("约瑟夫·葛兰碧 (Joseph Granville)",     "technical_masters/joseph-granville-perspective.md"),
    ("托马斯·德马克 (Thomas DeMark)",        "technical_masters/thomas-demark-perspective.md"),
    ("乔治·莱恩 (George Lane)",              "technical_masters/george-lane-perspective.md"),
    ("拉里·威廉姆斯 (Larry Williams)",       "technical_masters/larry-williams-perspective.md"),
    ("亚历山大·埃尔德 (Alexander Elder)",     "technical_masters/alexander-elder-perspective.md"),
    ("ARBR 团队",                            "technical_masters/japanese-sentiment-indicators-perspective.md"),
]

# ──────────────────────────────────────────────────────────────
# 阶段三：11 位技术指标大师（纯数字信号）
# 每个条目额外包含该大师关注的 indicator_keys 列表
# ──────────────────────────────────────────────────────────────

STAGE3_MASTERS = [
    ("Gerald Appel (MACD)",
     "signal_masters/gerald-appel-signal-perspective.md",
     ["MACD_12_26_9", "MACDh_12_26_9", "MACDs_12_26_9"]),

    ("John Bollinger (布林带)",
     "signal_masters/john-bollinger-signal-perspective.md",
     ["BBL_20_2.0", "BBM_20_2.0", "BBU_20_2.0"]),

    ("Joseph Granville (MA+OBV)",
     "signal_masters/joseph-granville-signal-perspective.md",
     ["SMA_5", "SMA_10", "SMA_20", "SMA_50", "SMA_200", "OBV"]),

    ("Goichi Hosoda (一目均衡)",
     "signal_masters/goichi-hosoda-signal-perspective.md",
     ["Ichimoku_Tenkan", "Ichimoku_Kijun", "Ichimoku_SpanA", "Ichimoku_SpanB"]),

    ("J. Welles Wilder (RSI/ADX/ATR/PSAR)",
     "signal_masters/welles-wilder-signal-perspective.md",
     ["RSI_14", "ADX_14", "DMP_14", "DMN_14", "ATRr_14"]),

    ("George Lane (KDJ)",
     "signal_masters/george-lane-signal-perspective.md",
     ["STOCHk_9_3_3", "STOCHd_9_3_3"]),

    ("Donald Lambert (CCI)",
     "signal_masters/donald-lambert-signal-perspective.md",
     ["CCI_20_0.015"]),

    ("Larry Williams (W%R)",
     "signal_masters/larry-williams-signal-perspective.md",
     ["WILLR_14"]),

    ("Marc Chaikin (CMF)",
     "signal_masters/marc-chaikin-signal-perspective.md",
     ["CMF_20"]),

    ("Alexander Elder (三重滤网)",
     "signal_masters/alexander-elder-signal-perspective.md",
     ["Force_Index_13", "Bull_Power", "Bear_Power", "EMA_12", "EMA_26"]),

    ("Bill Williams (混沌操作)",
     "signal_masters/bill-williams-signal-perspective.md",
     ["Alligator_Jaw", "Alligator_Teeth", "Alligator_Lips", "AO", "AC"]),
]
