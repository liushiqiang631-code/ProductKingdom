"""
最终产品生成器。
在五位大臣全部准奏后，根据原始需求和已批准奏折生成一个可运行的单文件 HTML 产品。
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from utils.llm import get_llm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = PROJECT_ROOT / "generated_products"


def get_product_dir(thread_id: str) -> Path:
    return PRODUCT_ROOT / thread_id


def get_product_html_path(thread_id: str) -> Path:
    return get_product_dir(thread_id) / "index.html"


def get_product_zip_path(thread_id: str) -> Path:
    return get_product_dir(thread_id) / "product.zip"


def product_exists(thread_id: str) -> bool:
    return get_product_html_path(thread_id).exists()


def build_product(thread_id: str, requirement: str, outputs: dict[str, str]) -> Path:
    """生成最终产品文件，若已存在则直接返回。"""
    html_path = get_product_html_path(thread_id)
    if html_path.exists():
        return html_path

    product_dir = get_product_dir(thread_id)
    product_dir.mkdir(parents=True, exist_ok=True)

    html = _generate_html(requirement, outputs)
    html_path.write_text(html, encoding="utf-8")

    docs_path = product_dir / "approved_documents.md"
    docs_path.write_text(_format_docs(requirement, outputs), encoding="utf-8")

    zip_path = get_product_zip_path(thread_id)
    if zip_path.exists():
        zip_path.unlink()
    temp_base = PRODUCT_ROOT / f"{thread_id}_package"
    temp_zip = Path(shutil.make_archive(str(temp_base), "zip", product_dir))
    temp_zip.replace(zip_path)

    return html_path


def _generate_html(requirement: str, outputs: dict[str, str]) -> str:
    context = _format_docs(requirement, outputs)
    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "你是一位资深全栈工程师。请根据产品需求和已批准设计，生成一个"
                    "可直接在浏览器运行的完整单文件 HTML 产品。"
                )
            ),
            HumanMessage(
                content=f"""
请生成最终可运行产品代码。

要求：
1. 只输出一个完整 HTML 文件的源码，不要解释，不要 Markdown 代码围栏。
2. 必须包含 <!doctype html>、HTML、CSS、JavaScript。
3. 所有样式和脚本都内联在同一个文件中，不依赖外部资源。
4. 如果用户需求是游戏或工具，必须做成真正可交互、可直接使用的版本。
5. 页面应包含清楚的标题、主要交互区、操作按钮、状态提示。
6. 代码应简洁稳健，中文界面优先。

【原始需求】
{requirement}

【已批准奏折】
{context}
"""
            ),
        ]
    )
    return _extract_html(response.content)


def _extract_html(text: str) -> str:
    """从模型输出中提取 HTML，兼容模型误加代码围栏的情况。"""
    cleaned = text.strip()
    fenced = re.search(r"```(?:html)?\s*(.*?)```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    doctype_index = cleaned.lower().find("<!doctype html")
    html_index = cleaned.lower().find("<html")
    start = doctype_index if doctype_index != -1 else html_index
    if start > 0:
        cleaned = cleaned[start:].strip()

    if "<html" not in cleaned.lower():
        cleaned = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ProductKingdom Generated Product</title>
</head>
<body>
<pre>{_escape_html(cleaned)}</pre>
</body>
</html>
"""
    return cleaned


def _format_docs(requirement: str, outputs: dict[str, str]) -> str:
    parts = [f"# 原始需求\n\n{requirement}"]
    for stage, content in outputs.items():
        parts.append(f"# {stage}\n\n{content}")
    return "\n\n---\n\n".join(parts)


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
