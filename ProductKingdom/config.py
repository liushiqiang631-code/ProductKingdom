"""
ProductKingdom 配置文件
从环境变量加载 API Key、模型名称、最大驳回次数等配置项。
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# ── LangSmith 追踪配置 ──
# 在 .env 中设置以下变量即可启用 LangSmith 自动追踪：
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=lsv2_pt_...
#   LANGCHAIN_PROJECT=ProductKingdom（可选，默认为 default）
#   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com（可选）
LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "")
LANGCHAIN_API_KEY_LS: str = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ProductKingdom")
LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "")

# OpenAI API Key（或其他兼容 LLM 的 Key）
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# LLM 模型名称，默认使用 DeepSeek V4 Flash
MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-v4-flash")

# API Base URL（用于自定义端点或兼容模型）
OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")

# LLM 调用最大 token 数
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

# 每份前序奏折注入 prompt 的最大字符数，避免上下文无限膨胀
CONTEXT_CHAR_LIMIT: int = int(os.getenv("CONTEXT_CHAR_LIMIT", "2000"))

# LLM 温度参数（0.0 ~ 1.0，越低越确定）
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

# 皇帝最大驳回次数，超过此次数强制通过
MAX_REVISIONS: int = int(os.getenv("MAX_REVISIONS", "3"))

# 阶段顺序定义（用于路由映射）
STAGE_ORDER: list[str] = ["pm", "architect", "backend", "frontend", "qa", "done"]

# 阶段中文名称映射
STAGE_NAMES: dict[str, str] = {
    "pm": "产品经理",
    "architect": "架构师",
    "backend": "后端开发",
    "frontend": "前端开发",
    "qa": "测试工程师",
    "done": "退朝",
}
