#!/usr/bin/env python3
"""
self_test.py

AI_Project_Example 的端到端自测。
验证所有工具是否正常工作，发现问题自动报告。

用法:
  python tools/scripts/self_test.py        ← 运行所有测试
  python tools/scripts/self_test.py --fix  ← 运行并自动修复可修复的问题
"""

import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = PROJECT_ROOT / "tools" / "scripts"
LAB_BOOK = PROJECT_ROOT / "lab_book"
WORKSPACE = PROJECT_ROOT / "workspace"

results = {"pass": 0, "fail": 0, "fix": 0, "errors": []}


def test(name, fn):
    """运行单个测试"""
    try:
        ok, msg = fn()
        if ok:
            results["pass"] += 1
            print(f"  ✅ {name}")
        else:
            results["fail"] += 1
            results["errors"].append(f"{name}: {msg}")
            print(f"  ❌ {name} — {msg}")
    except Exception as e:
        results["fail"] += 1
        results["errors"].append(f"{name}: {e}")
        print(f"  ❌ {name} — 异常: {e}")


# ── 基础设施测试 ──

def test_agents_md_exists():
    p = PROJECT_ROOT / "AGENTS.md"
    return (p.exists(), f"不存在")

def test_conventions_exists():
    p = PROJECT_ROOT / "CONVENTIONS.md"
    return (p.exists(), f"不存在")

def test_labbook_structure():
    for subdir in ["entries", "patterns", "mistakes"]:
        d = LAB_BOOK / subdir
        if not d.exists():
            return (False, f"lab_book/{subdir}/ 不存在")
        if not (d / "README.md").exists():
            return (False, f"lab_book/{subdir}/README.md 索引缺失")
    return (True, "")

def test_workspace_exists():
    return (WORKSPACE.exists(), "workspace/ 不存在")


# ── 工具测试 ──

def test_tool_importable(name):
    """测试工具脚本是否可以被 Python 加载（语法检查）"""
    def _test():
        path = TOOLS / f"{name}.py"
        if not path.exists():
            return (False, f"文件不存在")
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        # Don't execute, just compile
        import py_compile
        py_compile.compile(str(path), doraise=True)
        return (True, "")
    return _test

def test_agent_hub():
    """测试 agent_hub.py 是否能正常运行"""
    def _test():
        import subprocess
        r = subprocess.run(
            [sys.executable, str(TOOLS / "agent_hub.py"), "--quick"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return (False, r.stderr[:200])
        if "项目" not in r.stdout:
            return (False, "输出格式异常")
        return (True, "")
    return _test

def test_project_scanner():
    """测试 project_scanner.py"""
    def _test():
        import subprocess
        r = subprocess.run(
            [sys.executable, str(TOOLS / "project_scanner.py")],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return (False, r.stderr[:200])
        if "项目总数" not in r.stdout:
            return (False, "输出格式异常")
        return (True, "")
    return _test

def test_auto_evolve():
    """测试 auto_evolve.py"""
    def _test():
        import subprocess
        r = subprocess.run(
            [sys.executable, str(TOOLS / "auto_evolve.py"), "--detect"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return (False, r.stderr[:200])
        return (True, "")
    return _test

def test_knowledge_guard():
    """测试 knowledge_guard.py"""
    def _test():
        import subprocess
        r = subprocess.run(
            [sys.executable, str(TOOLS / "knowledge_guard.py")],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return (False, r.stderr[:200])
        return (True, "")
    return _test

def test_inbox_cleaner():
    """测试 inbox_cleaner.py"""
    def _test():
        # Find a project with inbox
        for item in WORKSPACE.iterdir():
            if item.is_dir() and (item / "inbox").exists():
                import subprocess
                r = subprocess.run(
                    [sys.executable, str(TOOLS / "inbox_cleaner.py"), str(item)],
                    capture_output=True, text=True, timeout=10,
                )
                if r.returncode != 0:
                    return (False, r.stderr[:200])
                return (True, "")
        return (True, "没有 inbox 项目，跳过")
    return _test

def test_tavern():
    """测试 ai_tavern 的 tavern.py"""
    def _test():
        tavern = WORKSPACE / "ai_tavern" / "scripts" / "tavern.py"
        if not tavern.exists():
            return (False, "tavern.py 不存在")
        import subprocess
        r = subprocess.run(
            [sys.executable, str(tavern), "status"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return (False, r.stderr[:200])
        return (True, "")
    return _test


# ── 知识库测试 ──

def test_patterns_have_index():
    p = LAB_BOOK / "patterns" / "README.md"
    if not p.exists():
        return (False, "patterns/README.md 不存在")
    content = p.read_text(encoding="utf-8")
    pattern_files = list((LAB_BOOK / "patterns").glob("*.md"))
    pattern_files = [f for f in pattern_files if f.name != "README.md"]
    indexed = content.count("|")
    if indexed < len(pattern_files):
        return (False, f"索引中有 {indexed} 条，实际有 {len(pattern_files)} 个 pattern")
    return (True, "")

def test_mistakes_all_resolved():
    mistakes_dir = LAB_BOOK / "mistakes"
    if not mistakes_dir.exists():
        return (True, "")
    for f in mistakes_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        content = f.read_text(encoding="utf-8")
        if "已解决" not in content and "✅" not in content:
            return (False, f"{f.name} 未标记解决")
    return (True, "")


# ── 修复功能 ──

def fix_missing_readmes():
    """修复缺失的 README 索引"""
    fixed = 0
    for subdir in ["entries", "patterns", "mistakes"]:
        d = LAB_BOOK / subdir
        if d.exists() and not (d / "README.md").exists():
            files = [f.stem for f in d.glob("*.md")]
            content = f"# {subdir} 索引\n\n" + "\n".join(f"- {f}" for f in files)
            (d / "README.md").write_text(content, encoding="utf-8")
            fixed += 1
    return fixed


def main():
    fix_mode = "--fix" in sys.argv

    print("🧪 AI_Project_Example 自测")
    print("=" * 50)

    print("\n📋 基础设施:")
    test("AGENTS.md 存在", test_agents_md_exists)
    test("CONVENTIONS.md 存在", test_conventions_exists)
    test("lab_book 结构完整", test_labbook_structure)
    test("workspace 存在", test_workspace_exists)

    print("\n🔧 工具脚本语法检查:")
    for script in sorted(TOOLS.glob("*.py")):
        test(f"{script.name} 语法正确", test_tool_importable(script.stem))

    print("\n🚀 工具运行测试:")
    test("agent_hub.py", test_agent_hub())
    test("project_scanner.py", test_project_scanner())
    test("auto_evolve.py", test_auto_evolve())
    test("knowledge_guard.py", test_knowledge_guard())
    test("inbox_cleaner.py", test_inbox_cleaner())
    test("tavern.py", test_tavern())

    print("\n📚 知识库:")
    test("patterns 索引完整", test_patterns_have_index)
    test("mistakes 全部已解决", test_mistakes_all_resolved)

    # Fix mode
    if fix_mode and results["fail"] > 0:
        print("\n🔧 尝试修复:")
        fixed = fix_missing_readmes()
        if fixed:
            results["fix"] = fixed
            print(f"  ✅ 修复了 {fixed} 个缺失的 README")

    # Summary
    print("\n" + "=" * 50)
    total = results["pass"] + results["fail"]
    print(f"📊 结果: {results['pass']}/{total} 通过, {results['fail']} 失败")
    if results["fix"]:
        print(f"🔧 修复: {results['fix']} 项")
    if results["fail"] == 0:
        print("🎉 全部通过！")
    else:
        print("\n❌ 失败项:")
        for e in results["errors"]:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
