"""
ProductKingdom —— 皇帝上朝式多 Agent 协作产品开发系统
入口文件：运行 CLI 交互循环

使用方法：
1. 配置 .env 文件（参见 .env.example）
2. pip install -r requirements.txt
3. python main.py
"""

import webbrowser
from langgraph.types import Command
from graph.workflow import compile_app
from config import STAGE_NAMES, LANGCHAIN_TRACING_V2, LANGCHAIN_PROJECT


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 60)
    print("🏯  ProductKingdom —— 皇帝上朝式产品开发系统")
    print("=" * 60)
    print("  五位大臣将依次启奏，请陛下批阅。")
    print("  输入 'y' 或 '准奏' 表示批准，其他输入为修改意见。")
    print("  输入 'quit' 退出朝堂。")

    # LangSmith 追踪状态
    if LANGCHAIN_TRACING_V2.lower() == "true":
        print(f"  🔍 LangSmith 追踪已启用 → 项目: {LANGCHAIN_PROJECT}")
        # 自动打开 LangSmith 面板
        try:
            langsmith_url = "https://smith.langchain.com"
            webbrowser.open(langsmith_url)
            print(f"  🌐 已打开 LangSmith 面板")
        except Exception:
            print(f"  📋 手动打开: https://smith.langchain.com")
    else:
        print("  ☐ LangSmith 追踪未启用（在 .env 中配置后自动激活）")

    print("=" * 60 + "\n")


def print_summary(outputs: dict[str, str]):
    """退朝后汇总打印所有已批准的奏折"""
    print("\n" + "=" * 60)
    print("📋  退朝汇总 —— 所有已批准的奏折")
    print("=" * 60)

    for stage_name, content in outputs.items():
        display_name = STAGE_NAMES.get(stage_name, stage_name)
        print(f"\n{'─' * 60}")
        print(f"📜 {display_name} 的奏折：")
        print(f"{'─' * 60}")
        print(content)
        print(f"{'─' * 60}")

    print(f"\n{'=' * 60}")
    print("🎉  所有大臣已启奏完毕，退朝！祝陛下产品大卖！")
    print("=" * 60 + "\n")


def display_draft(stage: str, draft: str):
    """展示当前大臣的奏折草案"""
    stage_name = STAGE_NAMES.get(stage, stage)
    print(f"\n{'=' * 60}")
    print(f"📜 {stage_name} 启奏：")
    print(f"{'=' * 60}")
    print(draft)
    print(f"{'=' * 60}")


def get_user_input() -> str:
    """获取并校验皇帝的朱批输入（空输入保护）"""
    while True:
        user_input = input(
            "\n👑 陛下朱批（'y'/'准奏'=批准，其他=修改意见，'quit'=退出）：\n> "
        ).strip()

        if user_input.lower() == "quit":
            return "quit"
        if user_input:
            return user_input
        print("⚠️ 输入不能为空，请陛下重新朱批。")


def has_interrupt(result: dict) -> bool:
    """检查 invoke 返回结果是否包含中断"""
    return isinstance(result, dict) and "__interrupt__" in result


def main():
    """主函数：运行皇帝上朝流程"""
    print_banner()

    # 编译图应用
    print("⏳ 正在初始化朝堂...")
    app = compile_app()
    print("✅ 朝堂已就绪。\n")

    # 请皇帝下旨
    requirement = input("👑 请陛下下旨（输入您的产品需求）：\n> ").strip()
    if not requirement:
        print("❌ 陛下未下旨，退朝。")
        return

    # 初始状态
    initial_state = {
        "requirement": requirement,
        "stage": "pm",
        "outputs": {},
        "current_draft": "",
        "feedback": "",
        "approval": False,
        "revision_count": {},
    }

    # 线程配置（checkpointer 需要）
    config = {"configurable": {"thread_id": "emperor-session-1"}}

    # ── 主循环 ──
    # invoke 遇到 interrupt 时返回 dict（含 __interrupt__），
    # 流程结束时返回纯 state dict（无 __interrupt__）。
    print("\n⏳ 大臣们正在准备启奏...\n")

    result = app.invoke(initial_state, config)

    while True:
        if has_interrupt(result):
            # ── 有中断：大臣已启奏，等待皇帝批阅 ──
            # 从 snapshot 中获取当前阶段和已提交的草案
            snapshot = app.get_state(config)
            state = snapshot.values
            stage = state.get("stage", "")
            draft = state.get("current_draft", "")

            # 展示奏折
            display_draft(stage, draft)

            # 获取皇帝朱批（含空输入保护）
            user_input = get_user_input()
            if user_input == "quit":
                print("\n🏯 陛下摆驾回宫，退朝！")
                return

            # 恢复图执行
            print("\n⏳ 正在传达圣意...\n")
            result = app.invoke(Command(resume=user_input), config)

        else:
            # ── 无中断：流程已完成 ──
            current_state = result
            stage = current_state.get("stage", "")
            if stage == "done":
                outputs = current_state.get("outputs", {})
                print_summary(outputs)
                break
            # 防御：不应走到这里
            print(f"⚠️ 异常状态: stage={stage}，无中断也未完成。")
            break

    print("\n✅ 流程结束。感谢陛下！")


if __name__ == "__main__":
    main()
