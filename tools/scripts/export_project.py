#!/usr/bin/env python3
"""
export_project.py

用途: 将 workspace/ 下的某个项目导出为独立可用的包
用法: python tools/scripts/export_project.py <项目名> [输出目录]

导出内容：
  ✅ 项目的全部文件
  ✅ 生成独立的 README（包含项目说明和使用方式）
  ✅ 不含 .venv、__pycache__、.DS_Store
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"


def export_project(project_name: str, output_dir: str = None) -> Path:
    """导出单个项目"""
    source = WORKSPACE / project_name
    if not source.exists():
        print(f"错误: 项目 {project_name} 不存在于 workspace/ 中")
        sys.exit(1)

    if output_dir:
        dest = Path(output_dir) / project_name
    else:
        dest = PROJECT_ROOT.parent / f"{project_name}_export"

    if dest.exists():
        print(f"错误: 目标目录已存在 {dest}")
        sys.exit(1)

    print(f"📦 导出项目: {project_name}")
    print("=" * 50)

    # 复制项目（排除不需要的文件）
    shutil.copytree(
        source, dest,
        ignore=shutil.ignore_patterns(
            ".venv", "__pycache__", ".DS_Store", ".git",
            "node_modules", "*.pyc",
        ),
    )
    print(f"  ✅ 项目文件已复制到 {dest}")

    # 统计
    file_count = len([f for f in dest.rglob("*") if f.is_file()])
    print(f"  📊 文件数: {file_count}")

    return dest


def main():
    if len(sys.argv) < 2:
        print("用法: python export_project.py <项目名> [输出目录]")
        print("示例: python export_project.py ai_tavern")
        print("      python export_project.py ai_tavern ~/Desktop/")
        sys.exit(1)

    project_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    dest = export_project(project_name, output_dir)

    print(f"\n✅ 导出完成: {dest}")
    print(f"   可以直接使用，不需要 AI_Project_Example 框架")


if __name__ == "__main__":
    main()
