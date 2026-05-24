"""
大师基类 — 所有 37 位大师的抽象父类。

提供:
    - 框架文件加载
    - LLM JSON 调用（含超时、降级、重试）
    - MasterOpinion 统一输出结构
"""

import os
import json
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

import config

logger = logging.getLogger(__name__)


# ─── 数据结构 ─────────────────────────────────────────────────

@dataclass
class MasterOpinion:
    """单个大师的分析结论（三阶段通用）。"""
    master_name: str
    stage: int                                       # 1 / 2 / 3
    stance: str                                      # bullish / bearish / neutral / avoid
    confidence: float                                # 0.0 ~ 1.0
    reasoning: str                                   # 核心推理文本
    key_levels: List[float] = field(default_factory=list)   # 支撑/阻力价位
    signals: List[str] = field(default_factory=list)        # 信号标签
    risk_warning: str = ""

    # 阶段一扩展
    valuation: Optional[Dict[str, Any]] = None

    # 阶段三扩展
    signal_strength: Optional[int] = None
    entry_target: Optional[float] = None
    stop_loss: Optional[float] = None
    target_high: Optional[float] = None
    target_low: Optional[float] = None


# ─── 基类 ─────────────────────────────────────────────────────

class BaseMaster:
    """
    大师基类。每个子类必须实现 ``analyze(context) -> MasterOpinion``。

    Args:
        name: 大师名称（中英混合）
        stage: 所属阶段（1 / 2 / 3）
        perspective_file: 框架文件相对路径（相对于 skill_references/）
    """

    def __init__(self, name: str, stage: int, perspective_file: str):
        self.name = name
        self.stage = stage

        # LLM client（懒初始化兼容缺失 openai 包）
        if AsyncOpenAI is not None and config.LLM_API_KEY:
            self.client = AsyncOpenAI(
                api_key=config.LLM_API_KEY,
                base_url=config.LLM_API_BASE,
            )
        else:
            self.client = None

        self.model = config.LLM_MODEL

        # 加载投资框架
        self.perspective_file = os.path.join(config.MASTER_REFERENCE_DIR, perspective_file)
        self.framework = self._load_framework()

    # ── 内部方法 ──────────────────────────────────────────────

    def _load_framework(self) -> str:
        """加载 .md 框架文件；文件缺失时返回降级 prompt。"""
        if not os.path.exists(self.perspective_file):
            logger.warning("框架文件缺失: %s", self.perspective_file)
            return f"你是 {self.name} 大师。请基于你的投资体系分析。"
        with open(self.perspective_file, 'r', encoding='utf-8') as f:
            return f.read()

    async def _call_llm_json(self, prompt: str, *,
                              system_prompt: str = "",
                              timeout: int = 60) -> dict:
        """
        调用 LLM 并解析 JSON 响应。

        失败场景统一降级为 ``_fallback_json()``。
        """
        if self.client is None:
            return self._fallback_json("LLM client not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                ),
                timeout=timeout,
            )
            content = response.choices[0].message.content
            return json.loads(content)

        except asyncio.TimeoutError:
            logger.warning("[%s] LLM 调用超时 (%ds)", self.name, timeout)
            return self._fallback_json("timeout")
        except json.JSONDecodeError:
            logger.warning("[%s] LLM 返回非法 JSON", self.name)
            return self._fallback_json("json_decode_error")
        except Exception as e:
            logger.error("[%s] LLM 调用异常: %s", self.name, e, exc_info=True)
            return self._fallback_json(f"error: {e}")

    @staticmethod
    def _fallback_json(reason: str) -> dict:
        """异常降级响应。"""
        return {
            "stance": "neutral",
            "confidence": 0.0,
            "reasoning": f"分析失败: {reason}",
            "key_levels": [],
            "signals": [],
            "risk_warning": "无法完成分析",
        }

    # ── 子类接口 ──────────────────────────────────────────────

    async def analyze(self, context: dict) -> MasterOpinion:
        """子类必须实现此方法。"""
        raise NotImplementedError(f"{self.__class__.__name__}.analyze() not implemented")
