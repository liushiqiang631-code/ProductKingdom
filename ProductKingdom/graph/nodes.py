"""
节点函数定义
包含所有工作节点（大臣）和审批节点（human_review_node）。
"""

from langgraph.types import interrupt
from config import MAX_REVISIONS


# ──────────────────────────────────────────────
# 工作节点：每位大臣的启奏逻辑
# ──────────────────────────────────────────────

def pm_node(state: dict) -> dict:
    """产品经理节点：生成或修改 PRD"""
    from agents.pm import generate
    draft = generate(state)
    return {
        "current_draft": draft,
        "stage": "pm",
        "approval": False,
        "feedback": "",
    }


def architect_node(state: dict) -> dict:
    """架构师节点：生成或修改系统架构设计"""
    from agents.architect import generate
    draft = generate(state)
    return {
        "current_draft": draft,
        "stage": "architect",
        "approval": False,
        "feedback": "",
    }


def backend_node(state: dict) -> dict:
    """后端开发节点：生成或修改接口与数据模型设计"""
    from agents.backend import generate
    draft = generate(state)
    return {
        "current_draft": draft,
        "stage": "backend",
        "approval": False,
        "feedback": "",
    }


def frontend_node(state: dict) -> dict:
    """前端开发节点：生成或修改页面与组件设计"""
    from agents.frontend import generate
    draft = generate(state)
    return {
        "current_draft": draft,
        "stage": "frontend",
        "approval": False,
        "feedback": "",
    }


def qa_node(state: dict) -> dict:
    """测试工程师节点：生成或修改测试方案"""
    from agents.qa import generate
    draft = generate(state)
    return {
        "current_draft": draft,
        "stage": "qa",
        "approval": False,
        "feedback": "",
    }


# ──────────────────────────────────────────────
# 审批节点：皇帝批阅奏折（human-in-the-loop）
# ──────────────────────────────────────────────

def human_review_node(state: dict) -> dict:
    """
    皇帝批阅节点。
    使用 LangGraph 的 interrupt 机制暂停执行，等待皇帝朱批。
    当外部通过 Command(resume=...) 恢复后，处理朱批意见。

    注意：interrupt() 只调用一次，空输入校验在 main.py 中完成。
    """
    stage = state["stage"]
    current_draft = state["current_draft"]
    revision_count = state.get("revision_count", {})
    current_revisions = revision_count.get(stage, 0)

    # ── 使用 interrupt 暂停图执行，等待皇帝朱批 ──
    # main.py 负责展示奏折并校验输入，这里只接收最终结果
    user_input = interrupt(current_draft)

    # ── 处理皇帝的朱批 ──
    user_input = (user_input or "").strip()

    # 判断是否批准
    if user_input.lower() in ("y", "准奏"):
        # 批准：将草案写入 outputs，推进阶段
        outputs = dict(state.get("outputs", {}))
        outputs[stage] = current_draft
        next_stage = _get_next_stage(stage)
        return {
            "outputs": outputs,
            "approval": True,
            "feedback": "",
            "stage": next_stage,
            "revision_count": revision_count,
        }
    else:
        # 驳回：记录反馈，增加驳回次数
        new_revisions = dict(revision_count)
        new_revisions[stage] = current_revisions + 1

        # 强制通过检查
        if new_revisions[stage] >= MAX_REVISIONS:
            print(
                f"\n⚠️ 陛下已驳回 {new_revisions[stage]} 次，"
                f"臣等不敢再辩，此奏折强制通过。\n"
            )
            outputs = dict(state.get("outputs", {}))
            outputs[stage] = current_draft
            next_stage = _get_next_stage(stage)
            return {
                "outputs": outputs,
                "approval": True,
                "feedback": "",
                "stage": next_stage,
                "revision_count": new_revisions,
            }

        # 未达上限：保留驳回意见，等待修改
        return {
            "approval": False,
            "feedback": user_input,
            "revision_count": new_revisions,
        }


def _get_next_stage(current_stage: str) -> str:
    """根据当前阶段返回下一阶段"""
    stage_map = {
        "pm": "architect",
        "architect": "backend",
        "backend": "frontend",
        "frontend": "qa",
        "qa": "done",
    }
    return stage_map.get(current_stage, "done")
