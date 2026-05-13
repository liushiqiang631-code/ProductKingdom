"""
前端开发（Frontend）Agent
负责生成页面设计、组件树和与后端交互方式。
"""

from langchain_core.messages import SystemMessage, HumanMessage
from utils.context import format_approved_outputs
from utils.llm import get_llm


def generate(state: dict) -> str:
    """
    前端开发生成奏折（页面设计、组件树、前后端交互）。
    """
    requirement = state["requirement"]
    outputs = state.get("outputs", {})
    feedback = state.get("feedback", "")
    current_draft = state.get("current_draft", "")

    context_text = format_approved_outputs(outputs)

    system_prompt = """你是一位资深前端开发工程师，正在向皇帝启奏前端设计方案。

你的职责是根据产品需求、架构设计和后端接口，设计用户界面和前端架构。

**输出格式要求**（使用 Markdown 多级标题）：

## 一、页面结构设计
列出所有页面/视图，说明每个页面的用途和主要内容区域。

## 二、组件树
以树形结构描述组件层级，说明每个组件的职责（如 Header、Sidebar、DataTable 等）。

## 三、状态管理方案
选择状态管理方案（如 Redux/Zustand/Pinia 等），描述核心状态结构。

## 四、与后端交互方式
描述 API 调用方式、数据获取策略（SWR/React Query 等）、错误处理。

## 五、页面路由设计
路由表设计，包含路径、对应页面组件、是否需要鉴权。

## 六、UI/UX 设计要点
交互规范、响应式策略、无障碍设计考虑。"""

    if feedback and current_draft:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

【上次奏折草案】
{current_draft}

【皇帝朱批意见】
{feedback}

请根据皇帝的朱批意见，对上次的前端设计进行修改完善。"""
    else:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

请根据需求、架构和后端接口，撰写完整的前端设计方案。"""

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])
    return response.content
