"""
KingdomState 定义
使用 TypedDict 定义 LangGraph 的共享状态结构。
"""

from typing import TypedDict


class KingdomState(TypedDict, total=False):
    """皇帝上朝系统的共享状态"""

    requirement: str
    """皇帝最初的产品需求描述"""

    stage: str
    """当前阶段，取值: pm / architect / backend / frontend / qa / done"""

    outputs: dict[str, str]
    """各位大臣已批准的奏折，key 为阶段名，value 为最终批准的文本"""

    current_draft: str
    """当前大臣刚刚启奏的草案（待皇帝审批）"""

    feedback: str
    """皇帝的朱批意见，驳回时为具体修改意见，批准时为空字符串"""

    approval: bool
    """当前草案是否被批准，仅作为中间流转标记"""

    revision_count: dict[str, int]
    """每个阶段被驳回的次数，key 为阶段名，value 为整数"""
