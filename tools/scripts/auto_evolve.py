#!/usr/bin/env python3
"""
auto_evolve.py

自动进化引擎：检测变更，触发对应的进化机制。

用法:
  python tools/scripts/auto_evolve.py              ← 检测并执行所有待处理的进化
  python tools/scripts/auto_evolve.py --detect     ← 只检测不执行
  python tools/scripts/auto_evolve.py --dry-run    ← 显示会做什么但不实际执行
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
LAB_BOOK = PROJECT_ROOT / "lab_book"


def detect_changes() -> list[dict]:
    """检测自上次检查以来的变更"""
    changes = []
    state_file = PROJECT_ROOT / "tools" / ".evolve_state.json"

    # Load last state
    last_state = {}
    if state_file.exists():
        last_state = json.loads(state_file.read_text(encoding="utf-8"))

    current_state = {}

    # Check workspace changes
    for item in WORKSPACE.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue
        mtime = max((f.stat().st_mtime for f in item.rglob("*") if f.is_file()), default=0)
        current_state[f"ws:{item.name}"] = mtime
        if mtime > last_state.get(f"ws:{item.name}", 0):
            changes.append({"type": "project_changed", "target": item.name})

    # Check lab_book changes
    for subdir in ["entries", "patterns", "mistakes"]:
        d = LAB_BOOK / subdir
        if d.exists():
            mtime = max((f.stat().st_mtime for f in d.glob("*.md") if f.name != "README.md"), default=0)
            current_state[f"lb:{subdir}"] = mtime
            if mtime > last_state.get(f"lb:{subdir}", 0):
                changes.append({"type": "labbook_changed", "target": subdir})

    # Check new projects without onboarding
    for item in WORKSPACE.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue
        entries = LAB_BOOK / "entries"
        if entries.exists():
            has_entry = any(item.name in f.name for f in entries.glob("*.md"))
            if not has_entry:
                changes.append({"type": "new_project", "target": item.name})

    # Check inbox backlogs
    for item in WORKSPACE.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue
        inbox = item / "inbox"
        if inbox.exists():
            count = len([f for f in inbox.rglob("*.md") if f.name != "README.md"])
            if count > 5:
                changes.append({"type": "inbox_backlog", "target": item.name, "count": count})

    # Save current state
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(current_state, indent=2), encoding="utf-8")

    return changes


def execute_evolution(changes: list[dict]) -> list[str]:
    """执行进化操作"""
    actions = []

    for change in changes:
        if change["type"] == "new_project":
            # Auto-create onboarding entry
            today = datetime.now().strftime("%Y-%m-%d")
            entry_path = LAB_BOOK / "entries" / f"{today}-{change['target']}-接入.md"
            if not entry_path.exists():
                entry_path.write_text(
                    f"# {today} {change['target']} 项目接入\n\n"
                    f"## 项目基本信息\n- 名称: {change['target']}\n- 阶段: 待补充\n",
                    encoding="utf-8",
                )
                actions.append(f"✅ 自动创建接入记录: {entry_path.name}")

        elif change["type"] == "inbox_backlog":
            actions.append(f"📬 {change['target']} inbox 积压 {change['count']} 条，建议清理")

        elif change["type"] == "project_changed":
            actions.append(f"📁 {change['target']} 有新变更")

        elif change["type"] == "labbook_changed":
            actions.append(f"📚 lab_book/{change['target']} 有新内容")

    return actions


def main():
    parser = argparse.ArgumentParser(description="自动进化引擎")
    parser.add_argument("--detect", action="store_true", help="只检测")
    parser.add_argument("--dry-run", action="store_true", help="预览不执行")
    args = parser.parse_args()

    changes = detect_changes()

    if not changes:
        print("✅ 没有检测到变更，无需进化。")
        return

    print(f"🔍 检测到 {len(changes)} 项变更:")
    for c in changes:
        print(f"  - {c['type']}: {c['target']}")

    if args.detect:
        return

    print()
    actions = execute_evolution(changes)

    if actions:
        print("🔧 执行的进化操作:")
        for a in actions:
            print(f"  {a}")
    else:
        print("ℹ️  没有需要自动执行的操作")


if __name__ == "__main__":
    main()
