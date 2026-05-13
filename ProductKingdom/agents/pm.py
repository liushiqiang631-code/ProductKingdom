"""
产品经理（PM）Agent
负责根据皇帝的需求生成产品需求文档（PRD）或用户故事。
"""

from langchain_core.messages import SystemMessage, HumanMessage
from utils.context import format_approved_outputs
from utils.llm import get_llm


def generate(state: dict) -> str:
    """
    产品经理生成奏折（PRD / 用户故事）。
    根据 state 中的需求、已批准的前序奏折和反馈（若有）生成或修改内容。
    """
    requirement = state["requirement"]
    outputs = state.get("outputs", {})
    feedback = state.get("feedback", "")
    current_draft = state.get("current_draft", "")

    # 构建已批准前序奏折的上下文，过长时自动截断
    context_text = format_approved_outputs(outputs)

    # 系统提示词：定义角色和输出格式
    system_prompt = """你是一位经验丰富的产品经理，正在向皇帝启奏产品需求文档。

你的职责是根据皇帝的旨意，撰写清晰、完整的产品需求文档。

**输出格式要求**（使用 Markdown 多级标题）：

## 一、背景与目标
简要说明产品背景、要解决的核心问题、预期目标。

## 二、用户故事
以"作为<角色>，我希望<功能>，以便<价值>"的格式，列出至少 3 个核心用户故事。

## 三、功能列表
以表格或列表形式，列出主要功能模块及其优先级（P0/P1/P2）。

## 四、非功能需求
性能、安全、可用性等方面的要求。

## 五、验收标准
明确产品交付的验收条件。"""

    # 构建用户消息
    if feedback and current_draft:
        # 有驳回意见：基于上次草案修改
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

【上次奏折草案】
{current_draft}

【皇帝朱批意见】
{feedback}

请根据皇帝的朱批意见，对上次的奏折进行修改完善。保留合理的部分，针对朱批意见重点改进。"""
    else:
        # 无驳回：全新生成
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

请根据以上需求和前序奏折，撰写完整的产品需求文档（PRD）。"""

    # 调用 LLM
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])
    return response.content
