#!/usr/bin/env python3
"""
inbox_cleaner.py

用途: 清理 inbox/ 中的积压记录，提示哪些可以加工
用法: python tools/scripts/inbox_cleaner.py <项目路径>

示例:
  python tools/scripts/inbox_cleaner.py workspace/political_philosophy
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def scan_inbox(project_path: Path) -> dict:
    """扫描 inbox 目录，统计待处理记录"""
    inbox = project_path / "inbox"
    if not inbox.exists():
        return {"error": f"inbox/ 目录不存在: {inbox}"}

    results = {
        "observations": [],
        "questions": [],
        "old_items": [],
    }

    today = datetime.now()
    cutoff = today - timedelta(days=7)

    for subdir in ["observations", "questions"]:
        dir_path = inbox / subdir
        if not dir_path.exists():
            continue
        for f in sorted(dir_path.glob("*.md")):
            if f.name == "README.md":
                continue
            # 尝试从文件名提取日期
            date_str = f.name[:10] if f.name[:4].isdigit() else None
            item = {
                "file": f.relative_to(PROJECT_ROOT),
                "name": f.stem,
                "date": date_str,
            }
            results[subdir].append(item)

            # 检查是否超过 7 天未处理
            if date_str:
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        results["old_items"].append(item)
                except ValueError:
                    pass

    return results


def main():
    if len(sys.argv) != 2:
        print("用法: python inbox_cleaner.py <项目路径>")
        print("示例: python inbox_cleaner.py workspace/political_philosophy")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    if not project_path.exists():
        print(f"错误: 路径不存在 {project_path}")
        sys.exit(1)

    results = scan_inbox(project_path)

    if "error" in results:
        print(f"❌ {results['error']}")
        sys.exit(1)

    total = len(results["observations"]) + len(results["questions"])
    print(f"📬 Inbox 状态: {project_path.name}")
    print("=" * 40)
    print(f"  现象记录: {len(results['observations'])} 条")
    print(f"  问题记录: {len(results['questions'])} 条")
    print(f"  总计: {total} 条")

    if results["old_items"]:
        print(f"\n⚠️  超过 7 天未处理的记录 ({len(results['old_items'])} 条):")
        for item in results["old_items"]:
            print(f"  - {item['name']} ({item['date']})")

    if total == 0:
        print("\n✅ Inbox 是空的，没有待处理记录。")
    elif not results["old_items"]:
        print("\n✅ 所有记录都在 7 天内，不需要紧急清理。")
    else:
        print(f"\n💡 建议: 有 {len(results['old_items'])} 条记录超过 7 天，考虑加工或归档。")


if __name__ == "__main__":
    main()
