"""
后端开发（Backend）Agent
负责根据需求和架构设计，生成接口设计、数据模型和核心逻辑说明。
"""

from langchain_core.messages import SystemMessage, HumanMessage
from utils.context import format_approved_outputs
from utils.llm import get_llm


def generate(state: dict) -> str:
    """
    后端开发生成奏折（接口设计、数据模型、核心逻辑）。
    """
    requirement = state["requirement"]
    outputs = state.get("outputs", {})
    feedback = state.get("feedback", "")
    current_draft = state.get("current_draft", "")

    context_text = format_approved_outputs(outputs)

    system_prompt = """你是一位经验丰富的后端开发工程师，正在向皇帝启奏后端设计方案。

你的职责是根据架构设计和产品需求，设计详细的接口、数据模型和核心业务逻辑。

**输出格式要求**（使用 Markdown 多级标题）：

## 一、数据模型设计
用类或表结构的形式定义核心数据模型（字段名、类型、约束、说明）。

## 二、API 接口详细设计
列出每个接口的：
- HTTP 方法与路径
- 请求参数（Query/Body）
- 响应格式
- 状态码
- 简要说明

## 三、核心业务逻辑
描述关键业务流程的实现逻辑，可用伪代码或流程描述。

## 四、数据库设计
表结构设计、索引策略、数据迁移方案（如适用）。

## 五、错误处理与安全
异常处理策略、鉴权方案、数据校验规则。"""

    if feedback and current_draft:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

【上次奏折草案】
{current_draft}

【皇帝朱批意见】
{feedback}

请根据皇帝的朱批意见，对上次的后端设计进行修改完善。"""
    else:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

请根据需求和架构设计，撰写完整的后端设计方案。"""

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])
    return response.content
