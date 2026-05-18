#!/usr/bin/env python3
"""
status_board.py

用途: 显示当前工作台的全局状态
用法: python tools/scripts/status_board.py

显示：项目状态、inbox 积压、最近活动、待处理事项
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
LAB_BOOK = PROJECT_ROOT / "lab_book"


def scan_projects() -> list[dict]:
    """扫描所有项目状态"""
    projects = []
    for item in sorted(WORKSPACE.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        info = {"name": item.name, "status": "unknown", "inbox_count": 0, "has_git": False}

        readme = item / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            if "status: active" in content:
                info["status"] = "active"
            elif "status: paused" in content:
                info["status"] = "paused"
            elif "status: archived" in content:
                info["status"] = "archived"

        # 统计 inbox
        inbox = item / "inbox"
        if inbox.exists():
            for f in inbox.rglob("*.md"):
                if f.name != "README.md":
                    info["inbox_count"] += 1

        if (item / ".project-gitconfig").exists():
            info["has_git"] = True

        projects.append(info)
    return projects


def scan_lab_book() -> dict:
    """扫描 lab_book 状态"""
    stats = {"entries": 0, "patterns": 0, "mistakes": 0}
    for subdir, key in [("entries", "entries"), ("patterns", "patterns"), ("mistakes", "mistakes")]:
        d = LAB_BOOK / subdir
        if d.exists():
            stats[key] = len(list(d.glob("*.md"))) - (1 if (d / "README.md").exists() else 0)
    return stats


def find_recent_activity(days: int = 3) -> list[str]:
    """查找最近 N 天的活动"""
    activities = []
    today = datetime.now()
    for f in LAB_BOOK.rglob("*.md"):
        if f.name == "README.md":
            continue
        # 从文件名提取日期
        date_str = f.name[:10] if f.name[:4].isdigit() else None
        if date_str:
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                delta = (today - file_date).days
                if delta <= days:
                    activities.append(f"[{date_str}] {f.stem}")
            except ValueError:
                pass
    return sorted(activities, reverse=True)


def main():
    projects = scan_projects()
    lb_stats = scan_lab_book()
    recent = find_recent_activity()

    print("📊 工作台状态看板")
    print("=" * 50)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 项目状态
    print(f"📁 项目 ({len(projects)} 个)")
    for p in projects:
        status_icon = {"active": "🟢", "paused": "🟡", "archived": "⚫"}.get(p["status"], "❓")
        git_icon = " 🔹git" if p["has_git"] else ""
        inbox_tag = f" 📬{p['inbox_count']}" if p["inbox_count"] > 0 else ""
        print(f"  {status_icon} {p['name']}{git_icon}{inbox_tag}")
    print()

    # 知识库状态
    print(f"📚 知识库")
    print(f"  记录条目: {lb_stats['entries']}")
    print(f"  经验模式: {lb_stats['patterns']}")
    print(f"  错误教训: {lb_stats['mistakes']}")
    print()

    # 最近活动
    if recent:
        print(f"🕐 最近 3 天活动")
        for a in recent[:10]:
            print(f"  {a}")
    else:
        print("🕐 最近 3 天没有活动记录")
    print()

    # 待处理事项
    inbox_total = sum(p["inbox_count"] for p in projects)
    if inbox_total > 0:
        print(f"⚠️  待处理: {inbox_total} 条 inbox 记录待加工")
    else:
        print("✅ inbox 已清空，没有待处理记录")


if __name__ == "__main__":
    main()
