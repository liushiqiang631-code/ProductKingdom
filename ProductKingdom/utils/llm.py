"""
LLM 实例创建工具
基于配置创建统一的 LLM 实例，供各 Agent 调用。
"""

from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASE, MODEL_NAME, MAX_TOKENS, TEMPERATURE


def get_llm() -> ChatOpenAI:
    """
    获取配置好的 LLM 实例。
    支持自定义 API Base（兼容 OpenAI 格式的其他模型服务）。
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "未配置 OPENAI_API_KEY。请在项目根目录创建 .env，并填入 DeepSeek API Key。"
        )

    kwargs = {
        "model": MODEL_NAME,
        "api_key": OPENAI_API_KEY,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    # 如果配置了自定义 API Base，则传入
    if OPENAI_API_BASE:
        kwargs["base_url"] = OPENAI_API_BASE
    return ChatOpenAI(**kwargs)
