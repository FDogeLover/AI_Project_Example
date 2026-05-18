#!/usr/bin/env python3
"""
knowledge_guard.py

用途: 检查 lab_book/ 中的记录是否过时或需要更新
用法: python tools/scripts/knowledge_guard.py

检查项：
1. 超过 N 天未更新的 pattern，提示检查是否过时
2. 检查 pattern 之间是否有矛盾
3. 检查 mistakes 是否已解决
"""

import sys
import re
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LAB_BOOK = PROJECT_ROOT / "lab_book"


def check_staleness(max_days: int = 90) -> list[dict]:
    """检查超过 N 天未更新的记录"""
    stale = []
    today = datetime.now()
    cutoff = today - timedelta(days=max_days)

    for subdir in ["patterns", "entries"]:
        d = LAB_BOOK / subdir
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            if f.name == "README.md":
                continue
            date_str = f.name[:10] if f.name[:4].isdigit() else None
            if date_str:
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if file_date < cutoff:
                        days_old = (today - file_date).days
                        stale.append({
                            "file": f.relative_to(PROJECT_ROOT),
                            "days_old": days_old,
                            "subdir": subdir,
                        })
                except ValueError:
                    pass
    return stale


def check_pattern_conflicts() -> list[tuple[str, str]]:
    """检查 pattern 之间是否有矛盾"""
    conflicts = []
    patterns_dir = LAB_BOOK / "patterns"
    if not patterns_dir.exists():
        return conflicts

    # 读取所有 pattern 的关键词
    pattern_contents = {}
    for f in patterns_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        content = f.read_text(encoding="utf-8").lower()
        pattern_contents[f.stem] = content

    # 简单的矛盾检测：如果两个 pattern 都包含"不要"和相同关键词
    names = list(pattern_contents.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_name, b_name = names[i], names[j]
            a_content = pattern_contents[a_name]
            b_content = pattern_contents[b_name]

            # 检查是否有"不要" vs "应该" 的矛盾
            a_donts = set(re.findall(r"不要(\w+)", a_content))
            b_donts = set(re.findall(r"不要(\w+)", b_content))
            a_should = set(re.findall(r"应该(\w+)", a_content))
            b_should = set(re.findall(r"应该(\w+)", b_content))

            # 如果 A 说"不要X" 而 B 说"应该X"
            contradictions = a_donts & b_should
            contradictions |= b_donts & a_should
            if contradictions:
                conflicts.append((a_name, b_name, contradictions))

    return conflicts


def check_mistakes_resolution() -> list[dict]:
    """检查 mistakes 是否标记为已解决"""
    unresolved = []
    mistakes_dir = LAB_BOOK / "mistakes"
    if not mistakes_dir.exists():
        return unresolved

    for f in mistakes_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        content = f.read_text(encoding="utf-8")
        if "已解决" not in content and "✅" not in content:
            unresolved.append({"file": f.relative_to(PROJECT_ROOT)})

    return unresolved


def main():
    print("🔍 知识保鲜检查")
    print("=" * 50)

    # 1. 过时检查
    stale = check_staleness()
    if stale:
        print(f"\n⚠️  超过 90 天未更新的记录 ({len(stale)} 条):")
        for s in stale:
            print(f"  - {s['file']} ({s['days_old']} 天前)")
    else:
        print("\n✅ 所有记录都在 90 天内，不需要更新")

    # 2. 矛盾检查
    conflicts = check_pattern_conflicts()
    if conflicts:
        print(f"\n⚠️  发现可能的矛盾 ({len(conflicts)} 对):")
        for a, b, words in conflicts:
            print(f"  - {a} vs {b}: 涉及关键词 {words}")
    else:
        print("\n✅ 没有发现矛盾的 pattern")

    # 3. 未解决的 mistakes
    unresolved = check_mistakes_resolution()
    if unresolved:
        print(f"\n⚠️  未标记解决的 mistakes ({len(unresolved)} 条):")
        for u in unresolved:
            print(f"  - {u['file']}")
    else:
        print("\n✅ 所有 mistakes 都已标记解决")

    print("\n" + "=" * 50)
    total_issues = len(stale) + len(conflicts) + len(unresolved)
    if total_issues == 0:
        print("🎉 知识库状态良好，无需处理")
    else:
        print(f"💡 共 {total_issues} 个问题需要关注")


if __name__ == "__main__":
    main()
