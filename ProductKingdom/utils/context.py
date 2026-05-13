"""
Agent 上下文整理工具。
将已批准奏折注入给后续大臣，同时限制单份奏折长度。
"""

from config import CONTEXT_CHAR_LIMIT


def format_approved_outputs(outputs: dict[str, str], limit: int = CONTEXT_CHAR_LIMIT) -> str:
    """格式化已批准奏折；过长内容截断并标明全文已存档。"""
    if not outputs:
        return "（暂无前序已批准奏折）"

    context_parts: list[str] = []
    for stage_name, content in outputs.items():
        text = content or ""
        if len(text) > limit:
            text = f"{text[:limit]}\n\n（奏折过长，全文已存档，此处仅展示前 {limit} 字）"
        context_parts.append(f"【{stage_name} 已批准奏折】\n{text}")

    return "\n\n".join(context_parts)
