#!/usr/bin/env python3
"""
daily_report.py

用途: 扫描今天的变更，自动生成工作摘要
用法: python tools/scripts/daily_report.py [日期]

示例:
  python tools/scripts/daily_report.py            # 今天
  python tools/scripts/daily_report.py 2026-05-15 # 指定日期
"""

import sys
import re
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LAB_BOOK = PROJECT_ROOT / "lab_book"
WORKSPACE = PROJECT_ROOT / "workspace"


def find_files_with_date(base_dir: Path, target_date: str) -> list[Path]:
    """在目录下查找文件名包含指定日期的文件"""
    results = []
    for f in base_dir.rglob("*.md"):
        if target_date in f.name:
            results.append(f)
    return results


def read_file_head(path: Path, max_lines: int = 10) -> str:
    """读取文件头部内容"""
    with open(path, encoding="utf-8") as f:
        lines = []
        for i, line in enumerate(f):
            if i >= max_lines:
                break
            lines.append(line.rstrip())
    return "\n".join(lines)


def find_modified_files(base_dir: Path, target_date: str) -> list[Path]:
    """查找今天修改过的文件（非文件名匹配，而是内容中包含日期）"""
    results = []
    for f in base_dir.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py", ".yaml", ".yml", ".json", ".toml"):
            try:
                content = f.read_text(encoding="utf-8")
                if target_date in content:
                    results.append(f)
            except Exception:
                pass
    return results


def generate_report(target_date: str) -> str:
    """生成工作日报"""
    report_lines = [
        f"# 工作日报 - {target_date}",
        "",
    ]

    # 1. lab_book 条目
    entries = find_files_with_date(LAB_BOOK / "entries", target_date)
    if entries:
        report_lines.append("## 今日记录")
        for entry in sorted(entries):
            rel_path = entry.relative_to(PROJECT_ROOT)
            preview = read_file_head(entry)
            report_lines.append(f"\n### {entry.stem}")
            report_lines.append(f"文件: {rel_path}")
            report_lines.append(f"\n{preview}")
            report_lines.append("")

    # 2. 错误记录
    mistakes = find_files_with_date(LAB_BOOK / "mistakes", target_date)
    if mistakes:
        report_lines.append("## 今日教训")
        for m in sorted(mistakes):
            rel_path = m.relative_to(PROJECT_ROOT)
            preview = read_file_head(m)
            report_lines.append(f"\n### {m.stem}")
            report_lines.append(f"文件: {rel_path}")
            report_lines.append(f"\n{preview}")
            report_lines.append("")

    # 3. 模式发现
    patterns = find_files_with_date(LAB_BOOK / "patterns", target_date)
    if patterns:
        report_lines.append("## 今日发现的模式")
        for p in sorted(patterns):
            report_lines.append(f"- {p.stem}")

    # 4. workspace 变更
    workspace_changes = find_modified_files(WORKSPACE, target_date)
    if workspace_changes:
        report_lines.append("## 今日工作空间变更")
        for wc in sorted(workspace_changes):
            rel_path = wc.relative_to(PROJECT_ROOT)
            report_lines.append(f"- {rel_path}")

    # 5. 汇总
    report_lines.append("")
    report_lines.append("## 汇总")
    report_lines.append(f"- 记录条目: {len(entries)}")
    report_lines.append(f"- 错误教训: {len(mistakes)}")
    report_lines.append(f"- 新发现模式: {len(patterns)}")
    report_lines.append(f"- 工作空间变更: {len(workspace_changes)}")

    if not any([entries, mistakes, patterns, workspace_changes]):
        report_lines.append("")
        report_lines.append("今天没有检测到变更记录。")

    return "\n".join(report_lines)


def main():
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = date.today().isoformat()

    # 验证日期格式
    if not re.match(r"\d{4}-\d{2}-\d{2}", target_date):
        print(f"错误: 日期格式不对 '{target_date}'，应为 YYYY-MM-DD")
        sys.exit(1)

    report = generate_report(target_date)
    print(report)

    # 同时保存到 lab_book/entries/
    output_file = LAB_BOOK / "entries" / f"{target_date}-daily-report.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding="utf-8")
    print(f"\n📄 报告已保存到: {output_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
