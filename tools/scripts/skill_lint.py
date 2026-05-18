#!/usr/bin/env python3
"""
skill_lint.py

用途: 自动检查 skill 的质量和完整性
用法: python tools/scripts/skill_lint.py <skill_path>

示例:
  python tools/scripts/skill_lint.py workspace/skill_factory/examples/example_proactive/
  python tools/scripts/skill_lint.py some_skill/
"""

import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 必须包含的章节
REQUIRED_SECTIONS = [
    "触发条件",
    "前置条件",
    "操作步骤",
    "常见坑点",
    "验证方法",
]

# 推荐包含的章节
RECOMMENDED_SECTIONS = [
    "相关 Skill",
]

# 质量规则
VAGUE_PATTERNS = [
    (r"注意\s*xxx", "坑点描述太模糊，写清楚具体问题"),
    (r"某个文件", "不要用'某个文件'，给出具体路径"),
    (r"适当的", "'适当的'不够具体，给明确的值或范围"),
    (r"相关配置", "'相关配置'不够具体，列出具体配置项"),
    (r"进行测试", "'进行测试'不够具体，给出测试命令"),
]

COMMAND_PATTERNS = [
    r"`[^`]*`",           # 反引号包裹的命令
    r"```[\s\S]*?```",    # 代码块
    r"(?:make|npm|pip|yarn|cargo|go|run)\s+\S+",  # 常见命令前缀
]


class LintResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_items = []

    def error(self, msg):
        self.errors.append(f"  ❌ {msg}")

    def warn(self, msg):
        self.warnings.append(f"  ⚠️  {msg}")

    def ok(self, msg):
        self.passed_items.append(f"  ✅ {msg}")

    @property
    def passed(self):
        return len(self.errors) == 0

    def summary(self):
        lines = []
        if self.errors:
            lines.append("❌ 错误 (必须修复):")
            lines.extend(self.errors)
        if self.warnings:
            lines.append("⚠️  警告 (建议修复):")
            lines.extend(self.warnings)
        if self.passed_items:
            lines.append("✅ 通过:")
            lines.extend(self.passed_items)

        total = len(self.errors) + len(self.warnings)
        if total == 0:
            lines.append("🎉 全部通过，没有发现问题！")
        else:
            lines.append(f"\n共 {len(self.errors)} 个错误，{len(self.warnings)} 个警告")

        return "\n".join(lines)


def lint_skill(skill_dir: Path) -> LintResult:
    """检查一个 skill 目录"""
    result = LintResult()
    skill_md = skill_dir / "SKILL.md"

    # 检查 SKILL.md 是否存在
    if not skill_md.exists():
        result.error("缺少 SKILL.md 文件")
        return result

    content = skill_md.read_text(encoding="utf-8")
    lines = content.split("\n")

    result.ok("SKILL.md 存在")

    # 检查 frontmatter
    if content.startswith("---"):
        result.ok("包含 frontmatter")
    else:
        result.warn("缺少 frontmatter (YAML 头部)")

    # 检查必须的章节
    for section in REQUIRED_SECTIONS:
        if section in content:
            result.ok(f"包含章节: {section}")
        else:
            result.error(f"缺少章节: {section}")

    # 检查推荐章节
    for section in RECOMMENDED_SECTIONS:
        if section in content:
            result.ok(f"包含推荐章节: {section}")
        else:
            result.warn(f"缺少推荐章节: {section}")

    # 检查模糊描述
    for pattern, msg in VAGUE_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            result.warn(f"模糊描述: {msg} (出现 {len(matches)} 次)")

    # 检查是否有代码块或命令
    has_code = bool(re.search(r"```", content))
    has_inline_code = bool(re.search(r"`[^`]+`", content))
    if has_code or has_inline_code:
        result.ok("包含代码/命令示例")
    else:
        result.warn("没有代码或命令示例，步骤可能不够具体")

    # 检查坑点数量
    gotcha_section = re.search(r"## 常见坑点([\s\S]*?)(?=\n## |\Z)", content)
    if gotcha_section:
        gotcha_text = gotcha_section.group(1)
        gotcha_count = len(re.findall(r"### 坑点", gotcha_text))
        if gotcha_count >= 2:
            result.ok(f"坑点数量充足: {gotcha_count} 个")
        elif gotcha_count >= 1:
            result.warn(f"坑点偏少: {gotcha_count} 个 (建议至少 2 个)")
        else:
            result.error("没有找到坑点 (必须至少 1 个)")

    # 检查步骤数量
    step_section = re.search(r"## 操作步骤([\s\S]*?)(?=\n## |\Z)", content)
    if step_section:
        step_text = step_section.group(1)
        step_count = len(re.findall(r"### 步骤", step_text))
        if step_count >= 1:
            result.ok(f"操作步骤: {step_count} 个")
        else:
            result.error("没有找到操作步骤")

    # 检查文件长度
    line_count = len(lines)
    if line_count <= 200:
        result.ok(f"文件长度合理: {line_count} 行")
    elif line_count <= 300:
        result.warn(f"文件偏长: {line_count} 行 (建议 200 行以内)")
    else:
        result.warn(f"文件太长: {line_count} 行 (考虑拆分)")

    # 检查 references/ 目录
    refs_dir = skill_dir / "references"
    if refs_dir.exists() and any(refs_dir.iterdir()):
        result.ok("references/ 目录存在且非空")
    else:
        result.warn("references/ 目录不存在或为空 (可选)")

    return result


def main():
    if len(sys.argv) != 2:
        print("用法: python skill_lint.py <skill_path>")
        print("示例: python skill_lint.py workspace/skill_factory/examples/example_proactive/")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"错误: 路径不存在 {skill_path}")
        sys.exit(1)

    print(f"🔍 检查 skill: {skill_path.name}")
    print("=" * 50)

    result = lint_skill(skill_path)
    print(result.summary())

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
