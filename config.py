"""全局配置（环境变量驱动）"""

import os
from dotenv import load_dotenv

load_dotenv()

__version__ = "1.0.0"

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
