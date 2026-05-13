"""
条件路由函数
根据审批结果决定下一步走向。
"""


def route_after_review(state: dict) -> str:
    """
    审批后的路由函数。
    - 若批准：根据当前 stage 路由到下一个工作节点。
    - 若驳回：路由回当前阶段的工作节点进行修改。
    """
    approval = state.get("approval", False)
    stage = state.get("stage", "")

    if approval:
        # 批准后，stage 已被推进到下一阶段
        # 需要根据新 stage 路由到对应的工作节点
        # 但注意：stage 在 review 节点中已被推进
        # 例如从 pm 批准后，stage 变为 architect
        # 此时应路由到 architect_node
        stage_node_map = {
            "architect": "architect_node",
            "backend": "backend_node",
            "frontend": "frontend_node",
            "qa": "qa_node",
            "done": "__end__",
        }
        return stage_node_map.get(stage, "__end__")
    else:
        # 驳回：回到当前阶段的工作节点修改
        stage_node_map = {
            "pm": "pm_node",
            "architect": "architect_node",
            "backend": "backend_node",
            "frontend": "frontend_node",
            "qa": "qa_node",
        }
        return stage_node_map.get(stage, "__end__")
