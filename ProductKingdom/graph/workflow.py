"""
LangGraph 工作流定义
构建"皇帝上朝"的完整状态图，包括所有节点、边和条件路由。
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import KingdomState
from graph.nodes import (
    pm_node,
    architect_node,
    backend_node,
    frontend_node,
    qa_node,
    human_review_node,
)
from graph.routing import route_after_review


def build_graph() -> StateGraph:
    """
    构建并编译"皇帝上朝"状态图。

    流程：
    START → pm_node → human_review_node → (条件路由)
    → architect_node → human_review_node → (条件路由)
    → backend_node → human_review_node → (条件路由)
    → frontend_node → human_review_node → (条件路由)
    → qa_node → human_review_node → (条件路由)
    → END

    条件路由：
    - 批准 → 进入下一阶段的工作节点
    - 驳回 → 回到当前阶段的工作节点修改
    """
    # 创建状态图
    workflow = StateGraph(KingdomState)

    # ── 添加工作节点 ──
    workflow.add_node("pm_node", pm_node)
    workflow.add_node("architect_node", architect_node)
    workflow.add_node("backend_node", backend_node)
    workflow.add_node("frontend_node", frontend_node)
    workflow.add_node("qa_node", qa_node)

    # ── 添加审批节点 ──
    workflow.add_node("human_review_node", human_review_node)

    # ── 入口边：从 START 到产品经理 ──
    workflow.add_edge(START, "pm_node")

    # ── 工作节点到审批节点的固定边 ──
    # 每位大臣启奏后，都交给皇帝批阅
    workflow.add_edge("pm_node", "human_review_node")
    workflow.add_edge("architect_node", "human_review_node")
    workflow.add_edge("backend_node", "human_review_node")
    workflow.add_edge("frontend_node", "human_review_node")
    workflow.add_edge("qa_node", "human_review_node")

    # ── 审批节点的条件边 ──
    # 根据皇帝的朱批决定下一步：批准则进入下一阶段，驳回则重新修改
    workflow.add_conditional_edges(
        "human_review_node",
        route_after_review,
        {
            "pm_node": "pm_node",
            "architect_node": "architect_node",
            "backend_node": "backend_node",
            "frontend_node": "frontend_node",
            "qa_node": "qa_node",
            "__end__": END,
        },
    )

    return workflow


def compile_app():
    """
    编译状态图，返回可执行的应用实例。
    使用 MemorySaver 作为 checkpointer（中断功能必需）。
    """
    workflow = build_graph()
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
