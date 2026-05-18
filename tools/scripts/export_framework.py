#!/usr/bin/env python3
"""
export_framework.py

用途: 导出 AI_Project_Example 框架本身（不含具体项目），供分享给他人
用法: python tools/scripts/export_framework.py [输出目录]

导出内容：
  ✅ AGENTS.md（AI 行为手册）
  ✅ CONVENTIONS.md（行为准则）
  ✅ .gitignore
  ✅ lab_book/（空结构 + 索引）
  ✅ tools/（脚本 + 模板）
  ✅ workspace/README.md（使用说明）

不导出：
  ❌ workspace/ 下的具体项目
  ❌ lab_book/ 下的具体记录
  ❌ .venv/、data/、models/
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def export_framework(output_dir: str = None) -> Path:
    """导出框架到指定目录"""
    if output_dir:
        dest = Path(output_dir)
    else:
        dest = PROJECT_ROOT.parent / f"AI_Project_Example_framework_{datetime.now().strftime('%Y%m%d')}"

    if dest.exists():
        print(f"⚠️  目标目录已存在: {dest}")
        print("请删除后重试，或指定其他目录。")
        sys.exit(1)

    dest.mkdir(parents=True)

    # 1. 核心文件
    for f in ["AGENTS.md", "CONVENTIONS.md", ".gitignore"]:
        src = PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, dest / f)
            print(f"  ✅ {f}")

    # 2. lab_book 空结构
    lb_dest = dest / "lab_book"
    for subdir in ["entries", "patterns", "mistakes"]:
        (lb_dest / subdir).mkdir(parents=True)
        # 复制 README 索引（不含具体内容）
        src_readme = PROJECT_ROOT / "lab_book" / subdir / "README.md"
        if src_readme.exists():
            shutil.copy2(src_readme, lb_dest / subdir / "README.md")
    # 复制 lab_book/README.md
    src_lb_readme = PROJECT_ROOT / "lab_book" / "README.md"
    if src_lb_readme.exists():
        shutil.copy2(src_lb_readme, lb_dest / "README.md")
    print(f"  ✅ lab_book/ (空结构)")

    # 3. tools/ 完整复制
    tools_dest = dest / "tools"
    shutil.copytree(PROJECT_ROOT / "tools", tools_dest)
    print(f"  ✅ tools/ (脚本 + 模板)")

    # 4. workspace/ 只复制 README
    ws_dest = dest / "workspace"
    ws_dest.mkdir()
    src_ws_readme = PROJECT_ROOT / "workspace" / "README.md"
    if src_ws_readme.exists():
        shutil.copy2(src_ws_readme, ws_dest / "README.md")
    print(f"  ✅ workspace/ (仅 README)")

    # 5. 生成使用说明
    usage = f"""# AI_Project_Example 框架

导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 使用方法

1. 将此目录放到你想要的位置
2. 按照 AGENTS.md 的指引开始使用
3. 在 workspace/ 下创建你的项目
4. 所有经验和教训记录到 lab_book/

## 包含内容

- AGENTS.md — AI 行为手册（核心）
- CONVENTIONS.md — 行为准则
- lab_book/ — 知识积累（空结构，开始使用后会自动填充）
- tools/ — 工具箱（创建项目、日报、质量检查等）
- workspace/ — 工作空间（空，放你的项目）

## 快速开始

```bash
# 创建第一个项目
python3 tools/scripts/new_project.py my_project backend

# 查看工作台状态
python3 tools/scripts/status_board.py

# 查看之前的经验教训
cat lab_book/mistakes/README.md
```
"""
    (dest / "QUICKSTART.md").write_text(usage, encoding="utf-8")
    print(f"  ✅ QUICKSTART.md")

    return dest


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else None
    print("📦 导出 AI_Project_Example 框架")
    print("=" * 50)

    dest = export_framework(output)

    print()
    print(f"✅ 框架已导出到: {dest}")
    print(f"   包含 {len(list(dest.rglob('*')))} 个文件/目录")
    print(f"   不含具体项目和数据，可以安全分享")


if __name__ == "__main__":
    main()
