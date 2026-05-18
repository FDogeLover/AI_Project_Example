#!/usr/bin/env python3
"""
import_project.py

用途: 将现有项目移植到 workspace/ 下，自动补充 AI_Project_Example 规范文件
用法: python tools/scripts/import_project.py <项目路径> [目标名称]

示例:
  python tools/scripts/import_project.py ~/my_existing_project
  python tools/scripts/import_project.py ~/my_existing_project new_name

流程:
  1. 扫描原项目结构和内容
  2. 复制到 workspace/<名称>/
  3. 自动检测 type（backend/frontend/ml/embedded/script/note/mixed）
  4. 补充 README.md（如果缺失或需要更新）
  5. 创建 notes/ 目录（如果缺失）
  6. 创建 .project-gitconfig（如果原项目有 .git）
  7. 生成移植报告
"""

import sys
import shutil
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"


def detect_type(project_dir: Path) -> str:
    """根据文件特征自动检测项目类型"""
    indicators = {
        "backend": [
            "requirements.txt", "pyproject.toml", "Gemfile", "go.mod",
            "pom.xml", "build.gradle", "Cargo.toml",
        ],
        "frontend": [
            "package.json", "tsconfig.json", "webpack.config.js",
            "vite.config.js", "angular.json", "next.config.js",
        ],
        "ml": [
            "notebooks/", "models/", "train.py", "model.py",
            "dataset", ".ipynb",
        ],
        "embedded": [
            "Makefile", "platformio.ini", "ino", "stm32",
            "arduino", "drivers/",
        ],
        "note": [],
    }

    # 统计匹配
    scores = {t: 0 for t in indicators}
    all_files = [f.name for f in project_dir.rglob("*") if f.is_file()]
    all_dirs = [d.name for d in project_dir.iterdir() if d.is_dir()]

    for type_name, checks in indicators.items():
        for check in checks:
            if check in all_files or check in all_dirs:
                scores[type_name] += 1

    # 检查是否主要是 markdown 文件
    md_count = sum(1 for f in all_files if f.endswith(".md"))
    total = len(all_files) if all_files else 1
    if md_count / total > 0.5:
        scores["note"] += 3

    # 返回得分最高的
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "mixed"
    return best


def scan_existing(project_dir: Path) -> dict:
    """扫描原项目的特征"""
    info = {
        "has_readme": False,
        "has_git": False,
        "has_notes": False,
        "has_tests": False,
        "has_requirements": False,
        "file_count": 0,
        "languages": set(),
        "structure": [],
    }

    for item in project_dir.iterdir():
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        if item.is_dir():
            info["structure"].append(item.name)
            if item.name == "notes":
                info["has_notes"] = True
            if item.name in ["tests", "test", "__tests__"]:
                info["has_tests"] = True
        elif item.is_file():
            info["file_count"] += 1
            if item.name == "README.md":
                info["has_readme"] = True
            if item.name in ["requirements.txt", "pyproject.toml", "setup.py"]:
                info["has_requirements"] = True

    # 检查 git
    if (project_dir / ".git").exists():
        info["has_git"] = True

    # 检测语言
    lang_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".rs": "rust", ".go": "go", ".c": "c", ".cpp": "cpp",
        ".java": "java", ".rb": "ruby",
    }
    for ext, lang in lang_map.items():
        count = sum(1 for f in project_dir.rglob(f"*{ext}") if f.is_file())
        if count > 0:
            info["languages"].add(f"{lang}({count})")

    return info


def import_project(source: str, target_name: str = None) -> None:
    """执行移植"""
    source_dir = Path(source).resolve()
    if not source_dir.exists():
        print(f"错误: 源路径不存在 {source_dir}")
        sys.exit(1)

    if target_name is None:
        target_name = source_dir.name

    target_dir = WORKSPACE / target_name
    if target_dir.exists():
        print(f"错误: 目标已存在 {target_dir}")
        print("请先删除或使用其他名称。")
        sys.exit(1)

    print(f"📦 移植项目: {source_dir.name} → workspace/{target_name}")
    print("=" * 50)

    # 1. 扫描原项目
    print("\n🔍 扫描原项目...")
    existing = scan_existing(source_dir)
    proj_type = detect_type(source_dir)
    print(f"  文件数: {existing['file_count']}")
    print(f"  目录: {', '.join(existing['structure'][:10])}")
    print(f"  语言: {', '.join(existing['languages']) or '未检测到'}")
    print(f"  自动检测类型: {proj_type}")
    print(f"  已有 README: {'是' if existing['has_readme'] else '否'}")
    print(f"  已有 Git: {'是' if existing['has_git'] else '否'}")
    print(f"  已有 tests: {'是' if existing['has_tests'] else '否'}")

    # 2. 复制到 workspace/
    print(f"\n📋 复制到 workspace/{target_name}...")
    shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".venv", "node_modules", ".DS_Store"
    ))
    print(f"  ✅ 复制完成")

    # 3. 补充 notes/ 目录
    if not existing["has_notes"]:
        (target_dir / "notes").mkdir(exist_ok=True)
        (target_dir / "notes" / "README.md").write_text(
            f"# {target_name} 项目记录\n\n本目录存放项目特有的记录。\n",
            encoding="utf-8",
        )
        print(f"  ✅ 创建 notes/ 目录")

    # 4. 补充 README.md
    if not existing["has_readme"]:
        from datetime import date
        readme_content = f"""# {target_name}

> type: {proj_type}
> status: active
> created: {date.today().isoformat()}
> imported: {date.today().isoformat()}

## 做什么
<!-- 从原项目补充说明 -->

## 技术栈
{', '.join(existing['languages']) or '待补充'}

## 从哪里移植
{source_dir}

## 进度日志
- {date.today().isoformat()} 从 {source_dir} 移植
"""
        (target_dir / "README.md").write_text(readme_content, encoding="utf-8")
        print(f"  ✅ 创建 README.md")
    else:
        # 在已有 README 中补充移植信息
        readme = target_dir / "README.md"
        content = readme.read_text(encoding="utf-8")
        if "imported" not in content:
            from datetime import date
            content += f"\n\n## 移植信息\n- 来源: {source_dir}\n- 移植日期: {date.today().isoformat()}\n"
            readme.write_text(content, encoding="utf-8")
            print(f"  ✅ 更新 README.md（添加移植信息）")

    # 5. 检查是否需要 Git
    print(f"\n🔧 Git 检查...")
    if existing["has_git"]:
        print(f"  原项目有 .git，建议单独管理 Git")
        print(f"  已跳过创建 .project-gitconfig")
    else:
        print(f"  原项目无 .git")
        print(f"  建议：在主仓库中管理，或手动创建 .project-gitconfig")

    # 6. 生成报告
    print(f"\n📊 移植报告")
    print("=" * 50)
    print(f"  来源: {source_dir}")
    print(f"  目标: {target_dir}")
    print(f"  类型: {proj_type}")
    print(f"  文件: {existing['file_count']} 个")
    print(f"  语言: {', '.join(existing['languages']) or '未检测到'}")
    print()
    print(f"  后续步骤:")
    print(f"  1. 编辑 {target_dir}/README.md 补充项目说明")
    print(f"  2. 确认类型是否正确（当前: {proj_type}）")
    if not existing["has_git"]:
        print(f"  3. 如需 Git，在 {target_dir}/ 创建 .project-gitconfig")


def main():
    if len(sys.argv) < 2:
        print("用法: python import_project.py <项目路径> [目标名称]")
        print("示例: python import_project.py ~/my_project")
        sys.exit(1)

    source = sys.argv[1]
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
    import_project(source, target_name)


if __name__ == "__main__":
    main()
