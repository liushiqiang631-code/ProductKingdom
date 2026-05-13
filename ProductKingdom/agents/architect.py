"""
架构师（Architect）Agent
负责根据需求和 PM 的奏折，生成系统架构设计与技术选型方案。
"""

from langchain_core.messages import SystemMessage, HumanMessage
from utils.context import format_approved_outputs
from utils.llm import get_llm


def generate(state: dict) -> str:
    """
    架构师生成奏折（系统架构设计）。
    """
    requirement = state["requirement"]
    outputs = state.get("outputs", {})
    feedback = state.get("feedback", "")
    current_draft = state.get("current_draft", "")

    # 构建已批准前序奏折的上下文，过长时自动截断
    context_text = format_approved_outputs(outputs)

    system_prompt = """你是一位资深系统架构师，正在向皇帝启奏系统架构设计方案。

你的职责是根据产品经理的需求文档，设计合理、可扩展的技术架构。

**输出格式要求**（使用 Markdown 多级标题）：

## 一、技术选型
列出前后端技术栈、数据库、中间件等选型，并说明选择理由。

## 二、模块划分
描述系统的模块/服务划分，各模块的职责边界。

## 三、数据流图（文字描述）
用文字描述核心业务的数据流向，包括用户请求到响应的完整链路。

## 四、接口设计概要
列出主要的 API 端点概要（RESTful 或 GraphQL），说明其用途。

## 五、部署架构
描述部署方案（单体/微服务/Serverless 等）、环境要求。

## 六、风险与权衡
列出技术风险、已知限制及应对策略。"""

    if feedback and current_draft:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

【上次奏折草案】
{current_draft}

【皇帝朱批意见】
{feedback}

请根据皇帝的朱批意见，对上次的架构设计进行修改完善。"""
    else:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

请根据需求文档，撰写完整的系统架构设计方案。"""

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])
    return response.content
