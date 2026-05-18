#!/usr/bin/env python3
"""
agent_hub.py

AI_Project_Example 的智能中枢。
Agent 接管时运行这个脚本，获取全局状态和下一步建议。

用法:
  python tools/scripts/agent_hub.py              ← 完整状态 + 建议
  python tools/scripts/agent_hub.py --quick      ← 快速状态（不给建议）
  python tools/scripts/agent_hub.py --health     ← 健康检查
  python tools/scripts/agent_hub.py --next       ← 只看下一步建议
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
LAB_BOOK = PROJECT_ROOT / "lab_book"
TOOLS = PROJECT_ROOT / "tools"


# ── 数据采集 ──

def scan_projects() -> list[dict]:
    """扫描所有项目"""
    projects = []
    if not WORKSPACE.exists():
        return projects
    for item in sorted(WORKSPACE.iterdir()):
        if not item.is_dir() or item.name.startswith("."):
            continue
        info = {"name": item.name, "type": None, "status": "active",
                "inbox": 0, "has_git": False, "has_notes": False}

        readme = item / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            import re
            m = re.search(r"type:\s*(\w+)", content)
            if m: info["type"] = m.group(1)
            if "status: paused" in content: info["status"] = "paused"
            if "status: archived" in content: info["status"] = "archived"

        if (item / ".project-gitconfig").exists(): info["has_git"] = True
        if (item / "notes").exists(): info["has_notes"] = True

        # Count inbox
        inbox = item / "inbox"
        if inbox.exists():
            info["inbox"] = len([f for f in inbox.rglob("*.md") if f.name != "README.md"])

        projects.append(info)
    return projects


def scan_lab_book() -> dict:
    """扫描 lab_book"""
    stats = {"entries": 0, "patterns": 0, "mistakes": 0, "unresolved": 0}
    for subdir, key in [("entries", "entries"), ("patterns", "patterns"), ("mistakes", "mistakes")]:
        d = LAB_BOOK / subdir
        if d.exists():
            files = [f for f in d.glob("*.md") if f.name != "README.md"]
            stats[key] = len(files)
            if key == "mistakes":
                for f in files:
                    content = f.read_text(encoding="utf-8")
                    if "已解决" not in content and "✅" not in content:
                        stats["unresolved"] += 1
    return stats


def check_health() -> dict:
    """健康检查"""
    issues = []

    # Check AGENTS.md exists and is recent
    agents_md = PROJECT_ROOT / "AGENTS.md"
    if not agents_md.exists():
        issues.append({"level": "error", "msg": "AGENTS.md 不存在"})
    elif agents_md.stat().st_size > 10000:
        issues.append({"level": "warn", "msg": f"AGENTS.md 偏大 ({agents_md.stat().st_size} bytes)"})

    # Check CONVENTIONS.md
    if not (PROJECT_ROOT / "CONVENTIONS.md").exists():
        issues.append({"level": "warn", "msg": "CONVENTIONS.md 不存在"})

    # Check lab_book structure
    for subdir in ["entries", "patterns", "mistakes"]:
        d = LAB_BOOK / subdir
        if not d.exists():
            issues.append({"level": "error", "msg": f"lab_book/{subdir}/ 不存在"})
        elif not (d / "README.md").exists():
            issues.append({"level": "warn", "msg": f"lab_book/{subdir}/README.md 索引缺失"})

    # Check tools
    scripts = list((TOOLS / "scripts").glob("*.py")) if (TOOLS / "scripts").exists() else []
    if len(scripts) < 3:
        issues.append({"level": "warn", "msg": f"tools/scripts/ 只有 {len(scripts)} 个脚本"})

    # Check projects without onboarding
    projects = scan_projects()
    for p in projects:
        entry = LAB_BOOK / "entries"
        if entry.exists():
            has_entry = any(p["name"] in f.name for f in entry.glob("*.md"))
            if not has_entry:
                issues.append({"level": "warn", "msg": f"项目 {p['name']} 没有接入记录"})

    return {"issues": issues, "healthy": len([i for i in issues if i["level"] == "error"]) == 0}


def generate_suggestions(projects: list[dict], lb_stats: dict, health: dict) -> list[str]:
    """生成下一步建议"""
    suggestions = []

    # Inbox backlogs (sorted by severity)
    backlog = [(p["name"], p["inbox"]) for p in projects if p["inbox"] > 3]
    for name, count in sorted(backlog, key=lambda x: -x[1]):
        suggestions.append(f"📬 {name} 有 {count} 条 inbox 待处理，建议加工")

    # Unresolved mistakes
    if lb_stats["unresolved"] > 0:
        suggestions.append(f"⚠️  有 {lb_stats['unresolved']} 条 mistakes 未标记解决")

    # Health errors
    for issue in health["issues"]:
        if issue["level"] == "error":
            suggestions.append(f"❌ {issue['msg']}")

    # Cross-project intelligence
    types = [p["type"] for p in projects if p["type"]]
    from collections import Counter
    type_counts = Counter(types)
    for t, count in type_counts.items():
        if count >= 2:
            suggestions.append(f"🔗 {t} 类项目有 {count} 个，可复用经验（运行 project_scanner.py 查看）")

    # Low pattern count
    if lb_stats["patterns"] < 10:
        suggestions.append(f"📝 经验模式 {lb_stats['patterns']} 个，建议多记录发现的规律")

    # Project count milestone
    if len(projects) >= 5:
        suggestions.append(f"🏗️  已有 {len(projects)} 个项目，考虑整理跨项目通用 skill")

    # Latest entry
    entries = LAB_BOOK / "entries"
    if entries.exists():
        recent = [f for f in entries.glob("*.md") if f.name != "README.md"]
        if recent:
            latest = sorted(recent, key=lambda f: f.name, reverse=True)[0]
            suggestions.append(f"🕐 最新记录: {latest.stem}")

    if not suggestions:
        suggestions.append("✅ 一切正常，没有需要立即处理的事项")

    return suggestions


# ── 输出 ──

def print_full_report(projects, lb_stats, health, suggestions):
    print("🏛️  AI_Project_Example 智能中枢")
    print("=" * 55)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # Projects
    print(f"📁 项目 ({len(projects)} 个)")
    for p in projects:
        icon = {"active": "🟢", "paused": "🟡", "archived": "⚫"}.get(p["status"], "❓")
        git = " 🔹" if p["has_git"] else ""
        inbox = f" 📬{p['inbox']}" if p["inbox"] > 0 else ""
        type_str = f" ({p['type']})" if p["type"] else ""
        print(f"  {icon} {p['name']}{type_str}{git}{inbox}")
    print()

    # Lab book
    print(f"📚 知识库: {lb_stats['entries']} 条目 / {lb_stats['patterns']} 模式 / {lb_stats['mistakes']} 教训")
    if lb_stats["unresolved"] > 0:
        print(f"  ⚠️  {lb_stats['unresolved']} 条教训未解决")
    print()

    # Health
    status = "✅ 健康" if health["healthy"] else "⚠️  有问题"
    print(f"🏥 系统状态: {status}")
    for issue in health["issues"]:
        level_icon = "❌" if issue["level"] == "error" else "⚠️"
        print(f"  {level_icon} {issue['msg']}")
    print()

    # Suggestions
    print("💡 下一步建议:")
    for s in suggestions:
        print(f"  {s}")
    print()


def print_quick(projects, lb_stats):
    print(f"📊 {len(projects)} 项目 | {lb_stats['entries']} 条目 | {lb_stats['patterns']} 模式 | {lb_stats['mistakes']} 教训")
    for p in projects:
        inbox = f"📬{p['inbox']}" if p["inbox"] > 0 else ""
        print(f"  {'🟢' if p['status']=='active' else '🟡'} {p['name']} {inbox}")


def print_health(health):
    status = "✅ 健康" if health["healthy"] else "⚠️  有问题"
    print(f"🏥 系统状态: {status}")
    for issue in health["issues"]:
        level_icon = "❌" if issue["level"] == "error" else "⚠️"
        print(f"  {level_icon} {issue['msg']}")
    if not health["issues"]:
        print("  没有发现问题")


def print_next(suggestions):
    print("💡 下一步建议:")
    for s in suggestions:
        print(f"  {s}")


def main():
    parser = argparse.ArgumentParser(description="AI_Project_Example 智能中枢")
    parser.add_argument("--quick", action="store_true", help="快速状态")
    parser.add_argument("--health", action="store_true", help="健康检查")
    parser.add_argument("--next", action="store_true", help="下一步建议")
    args = parser.parse_args()

    projects = scan_projects()
    lb_stats = scan_lab_book()
    health = check_health()
    suggestions = generate_suggestions(projects, lb_stats, health)

    if args.quick:
        print_quick(projects, lb_stats)
    elif args.health:
        print_health(health)
    elif args.next:
        print_next(suggestions)
    else:
        print_full_report(projects, lb_stats, health, suggestions)


if __name__ == "__main__":
    main()
