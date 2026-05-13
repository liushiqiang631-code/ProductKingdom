"""
ProductKingdom Web 入口。
提供一个宫廷风前端页面，并通过 Flask API 驱动 LangGraph human-in-the-loop 流程。
"""

from __future__ import annotations

from uuid import uuid4

from flask import Flask, abort, jsonify, render_template, request, send_file, send_from_directory
from langgraph.types import Command

from config import MAX_REVISIONS, STAGE_NAMES
from graph.workflow import compile_app
from utils.product_builder import (
    build_product,
    get_product_dir,
    get_product_html_path,
    get_product_zip_path,
    product_exists,
)


app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
graph_app = compile_app()


def _has_interrupt(result: dict) -> bool:
    return isinstance(result, dict) and "__interrupt__" in result


def _public_state(thread_id: str, result: dict | None = None) -> dict:
    """从 LangGraph snapshot 提取前端需要展示的状态。"""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph_app.get_state(config)
    state = snapshot.values or {}
    stage = state.get("stage", "")
    outputs = state.get("outputs", {})
    revision_count = state.get("revision_count", {})
    artifact_ready = product_exists(thread_id)

    return {
        "threadId": thread_id,
        "status": "review" if result is None or _has_interrupt(result) else "done",
        "stage": stage,
        "stageName": STAGE_NAMES.get(stage, stage),
        "draft": state.get("current_draft", ""),
        "outputs": outputs,
        "revisionCount": revision_count,
        "currentRevisions": revision_count.get(stage, 0),
        "maxRevisions": MAX_REVISIONS,
        "completedCount": len(outputs),
        "totalCount": 5,
        "artifactReady": artifact_ready,
        "artifact": {
            "sourceUrl": f"/api/product/{thread_id}/source",
            "useUrl": f"/products/{thread_id}/index.html",
            "downloadUrl": f"/api/product/{thread_id}/download",
        }
        if artifact_ready
        else None,
    }


def _error_response(exc: Exception, status_code: int = 500):
    return jsonify({"error": str(exc)}), status_code


def _ensure_product_artifact(thread_id: str) -> None:
    """流程完成后生成最终可运行产品文件。"""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph_app.get_state(config)
    state = snapshot.values or {}
    if state.get("stage") != "done":
        return
    build_product(thread_id, state.get("requirement", ""), state.get("outputs", {}))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/favicon.ico")
def favicon():
    return "", 204


@app.post("/api/start")
def start_session():
    payload = request.get_json(silent=True) or {}
    requirement = (payload.get("requirement") or "").strip()
    if not requirement:
        return jsonify({"error": "请先下旨，输入产品需求。"}), 400

    thread_id = uuid4().hex
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "requirement": requirement,
        "stage": "pm",
        "outputs": {},
        "current_draft": "",
        "feedback": "",
        "approval": False,
        "revision_count": {},
    }

    try:
        result = graph_app.invoke(initial_state, config)
        return jsonify(_public_state(thread_id, result))
    except Exception as exc:
        return _error_response(exc)


@app.post("/api/review")
def review_draft():
    payload = request.get_json(silent=True) or {}
    thread_id = (payload.get("threadId") or "").strip()
    verdict = (payload.get("verdict") or "").strip()
    feedback = (payload.get("feedback") or "").strip()

    if not thread_id:
        return jsonify({"error": "会话已失效，请重新开始。"}), 400

    user_input = "准奏" if verdict == "approve" else feedback
    if not user_input:
        return jsonify({"error": "驳回时必须填写朱批意见。"}), 400

    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = graph_app.invoke(Command(resume=user_input), config)
        if not _has_interrupt(result):
            _ensure_product_artifact(thread_id)
        data = _public_state(thread_id, result)
        if not _has_interrupt(result) and data["stage"] == "done":
            data["status"] = "done"
        return jsonify(data)
    except Exception as exc:
        return _error_response(exc)


@app.get("/api/product/<thread_id>/source")
def product_source(thread_id: str):
    html_path = get_product_html_path(thread_id)
    if not html_path.exists():
        return jsonify({"error": "产品源码尚未生成。请先完成五位大臣的奏折审批。"}), 404
    return jsonify({"filename": "index.html", "code": html_path.read_text(encoding="utf-8")})


@app.get("/api/product/<thread_id>/download")
def product_download(thread_id: str):
    zip_path = get_product_zip_path(thread_id)
    if not zip_path.exists():
        return jsonify({"error": "产品下载包尚未生成。"}), 404
    return send_file(zip_path, as_attachment=True, download_name="ProductKingdom-product.zip")


@app.get("/products/<thread_id>/<path:filename>")
def product_file(thread_id: str, filename: str):
    product_dir = get_product_dir(thread_id)
    resolved = (product_dir / filename).resolve()
    if not str(resolved).startswith(str(product_dir.resolve())) or not resolved.exists():
        abort(404)
    return send_from_directory(product_dir, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False)
