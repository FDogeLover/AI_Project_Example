#!/usr/bin/env python3
"""
new_project.py

用途: 在 workspace/ 下一键创建新项目，自动完成接入流程
用法: python tools/scripts/new_project.py <project_name> <type>

类型选项: backend, frontend, ml, embedded, script, note, mixed

示例:
  python tools/scripts/new_project.py my_api backend
  python tools/scripts/new_project.py cifar_experiment ml
  python tools/scripts/new_project.py political_philosophy note
"""

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
LAB_BOOK = PROJECT_ROOT / "lab_book"

VALID_TYPES = ["backend", "frontend", "ml", "embedded", "script", "note", "mixed"]

TYPE_STRUCTURES = {
    "backend": ["src/", "tests/", "docs/", "scripts/", "notes/"],
    "frontend": ["src/", "public/", "tests/", "docs/", "notes/"],
    "ml": ["data/", "notebooks/", "src/", "models/", "configs/", "scripts/", "notes/"],
    "embedded": ["src/", "drivers/", "configs/", "docs/", "notes/"],
    "script": ["src/", "configs/", "docs/", "notes/"],
    "note": ["inbox/observations/", "inbox/questions/", "knowledge/patterns/",
             "knowledge/cases/", "knowledge/theories/", "connections/", "notes/"],
    "mixed": ["src/", "docs/", "scripts/", "notes/"],
}

TYPE_HINTS = {
    "backend": "Web 后端 / API 服务",
    "frontend": "前端应用 / Web UI",
    "ml": "机器学习 / 深度学习实验",
    "embedded": "嵌入式 / 单片机项目",
    "script": "自动化脚本 / 工具",
    "note": "文档 / 知识体系",
    "mixed": "混合型项目",
}


def create_project(name: str, proj_type: str) -> None:
    """创建项目并自动完成接入流程"""
    project_dir = WORKSPACE / name

    if project_dir.exists():
        print(f"错误: {name} 已存在于 {project_dir}")
        sys.exit(1)

    today = date.today().isoformat()
    hint = TYPE_HINTS.get(proj_type, "待定")

    # 1. 创建目录结构
    project_dir.mkdir(parents=True)
    for subdir in TYPE_STRUCTURES.get(proj_type, TYPE_STRUCTURES["mixed"]):
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    # 2. 生成 README.md
    subdirs = "\n".join(f"- `{d}`" for d in TYPE_STRUCTURES.get(proj_type, []))
    readme_content = f"""# {name}

> type: {proj_type}
> status: active
> created: {today}
> last_active: {today}

## 做什么
<!-- 一句话说明这个项目的目标 -->

## 技术栈
<!-- 列出使用的核心技术 -->

## 目录结构

{subdirs}

## 当前阶段
刚开始

## 进度日志
- {today} 项目创建
"""
    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 3. 生成 notes/progress.md
    progress_content = f"""# {name} 进度

## {today}
- 项目创建（type: {proj_type}）
"""
    (project_dir / "notes" / "progress.md").write_text(progress_content, encoding="utf-8")

    # 4. 生成 lab_book 接入记录
    entry_content = f"""# {today} {name} 项目接入

## 项目基本信息
- 名称: {name}
- 类型: {proj_type}
- 阶段: 刚开始
- 技术栈: 待补充

## 设计决策
待补充

## 后续关注点
待补充
"""
    entry_path = LAB_BOOK / "entries" / f"{today}-{name}-接入.md"
    entry_path.write_text(entry_content, encoding="utf-8")

    # 5. 汇总输出
    print(f"✅ 项目 {name} 已创建并完成接入")
    print(f"   类型: {proj_type} ({hint})")
    print(f"   目录: {project_dir}")
    print(f"   接入记录: {entry_path.relative_to(PROJECT_ROOT)}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {project_dir}/README.md 补充项目说明")
    print(f"  2. 在对话中向 AI 介绍这个项目（AI 会自动提问和建议）")


def main():
    if len(sys.argv) != 3:
        print("用法: python new_project.py <project_name> <type>")
        print(f"类型: {', '.join(VALID_TYPES)}")
        sys.exit(1)

    name = sys.argv[1]
    proj_type = sys.argv[2]

    if proj_type not in VALID_TYPES:
        print(f"错误: 无效类型 '{proj_type}'")
        print(f"可选: {', '.join(VALID_TYPES)}")
        sys.exit(1)

    create_project(name, proj_type)


if __name__ == "__main__":
    main()
