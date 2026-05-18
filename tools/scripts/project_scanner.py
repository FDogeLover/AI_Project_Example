#!/usr/bin/env python3
"""
project_scanner.py

用途: 扫描 workspace/ 中所有项目，发现共性和可复用的经验
用法: python tools/scripts/project_scanner.py [新项目名]

示例:
  python tools/scripts/project_scanner.py                    # 扫描所有项目
  python tools/scripts/project_scanner.py new_project_name   # 扫描并对比新项目
"""

import sys
import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"


def scan_project(project_dir: Path) -> dict:
    """扫描单个项目的元信息"""
    info = {
        "name": project_dir.name,
        "type": None,
        "tech_stack": [],
        "structure": [],
        "has_git": False,
        "has_notes": False,
        "has_readme": False,
    }

    # 读取 README 获取 type 和技术栈
    readme = project_dir / "README.md"
    if readme.exists():
        info["has_readme"] = True
        content = readme.read_text(encoding="utf-8")
        # 提取 type
        type_match = re.search(r"type:\s*(\w+)", content)
        if type_match:
            info["type"] = type_match.group(1)
        # 提取技术栈关键词
        tech_keywords = ["python", "pytorch", "tensorflow", "fastapi", "react",
                         "vue", "vuejs", "typescript", "javascript", "rust",
                         "go", "golang", "docker", "postgresql", "mysql",
                         "redis", "mongodb", "sqlalchemy", "numpy", "pandas"]
        for kw in tech_keywords:
            if kw.lower() in content.lower():
                info["tech_stack"].append(kw)

    # 扫描目录结构
    for item in sorted(project_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            info["structure"].append(item.name)

    # 检查 Git
    if (project_dir / ".project-gitconfig").exists():
        info["has_git"] = True

    # 检查 notes
    if (project_dir / "notes").exists():
        info["has_notes"] = True

    return info


def find_similarities(projects: list[dict]) -> dict:
    """发现项目间的共性"""
    similarities = {
        "shared_types": Counter(),
        "shared_tech": Counter(),
        "shared_structure": Counter(),
        "cross_project_tech_pairs": [],
    }

    for p in projects:
        if p["type"]:
            similarities["shared_types"][p["type"]] += 1
        for tech in p["tech_stack"]:
            similarities["shared_tech"][tech] += 1
        for struct in p["structure"]:
            similarities["shared_structure"][struct] += 1

    # 发现跨项目技术组合
    tech_combos = Counter()
    for p in projects:
        if len(p["tech_stack"]) >= 2:
            combo = tuple(sorted(p["tech_stack"]))
            tech_combos[combo] += 1
    similarities["cross_project_tech_pairs"] = [
        (combo, count) for combo, count in tech_combos.most_common(5)
    ]

    return similarities


def suggest_reuse(new_project_name: str, projects: list[dict], similarities: dict) -> list[str]:
    """为新项目推荐可复用的经验"""
    suggestions = []

    # 查找相同类型的项目
    for p in projects:
        if p["name"] == new_project_name:
            continue
        # 如果有相同 type 的项目，推荐参考其结构
        if p["type"]:
            suggestions.append(
                f"发现相同类型的项目: {p['name']} (type: {p['type']})，"
                f"可以参考其目录结构: {', '.join(p['structure'][:5])}"
            )

    # 查找使用相同技术的项目
    new_project = next((p for p in projects if p["name"] == new_project_name), None)
    if new_project:
        for p in projects:
            if p["name"] == new_project_name:
                continue
            common_tech = set(p["tech_stack"]) & set(new_project["tech_stack"])
            if common_tech:
                suggestions.append(
                    f"与 {p['name']} 共享技术栈: {', '.join(common_tech)}，"
                    f"可以复用其代码模式和经验"
                )

    # 推荐 lab_book 中的经验
    lab_book_patterns = PROJECT_ROOT / "lab_book" / "patterns"
    if lab_book_patterns.exists():
        pattern_files = list(lab_book_patterns.glob("*.md"))
        if pattern_files:
            suggestions.append(
                f"lab_book/patterns/ 中有 {len(pattern_files)} 个已沉淀的模式，"
                f"建议在动手前先查阅"
            )

    return suggestions


def print_report(projects: list[dict], similarities: dict, suggestions: list[str] = None):
    """打印扫描报告"""
    print(f"📊 工作台扫描报告")
    print("=" * 50)
    print(f"项目总数: {len(projects)}")
    print()

    # 项目概览
    print("项目列表:")
    for p in projects:
        git_tag = " 🔹git" if p["has_git"] else ""
        print(f"  - {p['name']} (type: {p['type'] or '未定义'}){git_tag}")
    print()

    # 类型分布
    if similarities["shared_types"]:
        print("类型分布:")
        for t, count in similarities["shared_types"].most_common():
            print(f"  - {t}: {count} 个项目")
        print()

    # 技术栈分布
    if similarities["shared_tech"]:
        print("技术栈分布:")
        for tech, count in similarities["shared_tech"].most_common(10):
            print(f"  - {tech}: {count} 个项目使用")
        print()

    # 结构共性
    if similarities["shared_structure"]:
        print("目录结构共性:")
        for struct, count in similarities["shared_structure"].most_common():
            if count >= 2:
                print(f"  - {struct}/: {count} 个项目都有")
        print()

    # 推荐
    if suggestions:
        print("💡 可复用经验:")
        for s in suggestions:
            print(f"  - {s}")


def main():
    # 扫描所有项目
    projects = []
    if WORKSPACE.exists():
        for item in sorted(WORKSPACE.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                projects.append(scan_project(item))

    if not projects:
        print("workspace/ 中没有找到项目。")
        sys.exit(0)

    similarities = find_similarities(projects)

    # 如果指定了新项目名，生成推荐
    suggestions = None
    if len(sys.argv) > 1:
        new_name = sys.argv[1]
        suggestions = suggest_reuse(new_name, projects, similarities)

    print_report(projects, similarities, suggestions)


if __name__ == "__main__":
    main()
