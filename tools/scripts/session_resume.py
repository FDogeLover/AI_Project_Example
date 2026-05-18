#!/usr/bin/env python3
"""
session_resume.py

用途: 生成"上次工作恢复点"，让新 session 快速接续
用法: python tools/scripts/session_resume.py

输出：当前工作台快照，包括进行中的项目、未完成的事项、最近的变更
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
LAB_BOOK = PROJECT_ROOT / "lab_book"


def get_latest_entry(subdir: str) -> tuple[str, str] | None:
    """获取某个子目录中最新的条目"""
    d = LAB_BOOK / subdir
    if not d.exists():
        return None
    files = sorted(
        [f for f in d.glob("*.md") if f.name != "README.md"],
        key=lambda f: f.name,
        reverse=True,
    )
    if files:
        return (files[0].name, files[0].read_text(encoding="utf-8")[:200])
    return None


def get_active_projects() -> list[dict]:
    """获取活跃项目列表"""
    projects = []
    for item in sorted(WORKSPACE.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        readme = item / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            if "status: active" in content:
                # 读取进度
                progress = item / "notes" / "progress.md"
                progress_text = ""
                if progress.exists():
                    progress_text = progress.read_text(encoding="utf-8")[:300]
                projects.append({"name": item.name, "progress": progress_text})
    return projects


def main():
    print("🔄 会话恢复点")
    print("=" * 50)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 活跃项目
    projects = get_active_projects()
    print(f"📁 活跃项目 ({len(projects)} 个)")
    for p in projects:
        print(f"\n  【{p['name']}】")
        if p["progress"]:
            for line in p["progress"].strip().split("\n")[:5]:
                print(f"    {line}")
    print()

    # 最新记录
    for subdir, title in [("entries", "最新记录"), ("mistakes", "最新教训"), ("patterns", "最新模式")]:
        result = get_latest_entry(subdir)
        if result:
            name, preview = result
            print(f"📝 {title}: {name}")
            for line in preview.strip().split("\n")[:3]:
                print(f"  {line}")
            print()

    # 未完成事项
    inbox_total = 0
    for item in WORKSPACE.iterdir():
        if not item.is_dir() or item.name.startswith("."):
            continue
        inbox = item / "inbox"
        if inbox.exists():
            count = len([f for f in inbox.rglob("*.md") if f.name != "README.md"])
            if count > 0:
                inbox_total += count
                print(f"📬 {item.name} 有 {count} 条 inbox 待处理")

    if inbox_total == 0:
        print("✅ 没有待处理的 inbox 记录")

    print()
    print("=" * 50)
    print("💡 以上是上次工作的快照，可以据此决定接下来做什么")


if __name__ == "__main__":
    main()
