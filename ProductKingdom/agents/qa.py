"""
测试工程师（QA）Agent
负责生成测试计划、测试用例和验收标准。
"""

from langchain_core.messages import SystemMessage, HumanMessage
from utils.context import format_approved_outputs
from utils.llm import get_llm


def generate(state: dict) -> str:
    """
    测试工程师生成奏折（测试计划、测试用例、验收标准）。
    """
    requirement = state["requirement"]
    outputs = state.get("outputs", {})
    feedback = state.get("feedback", "")
    current_draft = state.get("current_draft", "")

    context_text = format_approved_outputs(outputs)

    system_prompt = """你是一位严谨的测试工程师，正在向皇帝启奏测试方案。

你的职责是根据所有前序奏折（需求、架构、后端、前端），制定全面的测试策略。

**输出格式要求**（使用 Markdown 多级标题）：

## 一、测试策略概述
说明测试范围、测试类型（单元/集成/E2E/性能/安全）、测试优先级。

## 二、测试环境
测试环境需求、测试数据准备方案、Mock 策略。

## 三、核心功能测试用例
以表格形式列出关键测试用例：
| 用例ID | 模块 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 | 优先级 |

至少列出 10 个核心测试用例。

## 四、边界与异常测试
边界值、异常输入、并发场景、网络异常等测试用例。

## 五、验收标准
定义明确的验收条件（Acceptance Criteria），哪些条件满足才能判定为通过。

## 六、回归测试方案
回归范围、自动化测试策略、持续集成中的测试流程。"""

    if feedback and current_draft:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

【上次奏折草案】
{current_draft}

【皇帝朱批意见】
{feedback}

请根据皇帝的朱批意见，对上次的测试方案进行修改完善。"""
    else:
        user_msg = f"""皇帝的原始需求：
{requirement}

已批准的前序奏折：
{context_text}

请根据所有已批准的奏折，撰写完整的测试方案。"""

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])
    return response.content
