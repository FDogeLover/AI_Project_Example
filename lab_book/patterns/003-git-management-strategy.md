# Git 管理策略

## 什么时候需要 Git

```
需要 Git 的项目：
  ✅ 持续开发中的项目（有多个版本迭代）
  ✅ 有实际产出的项目（代码、文档、数据）
  ✅ 需要多人协作的项目
  ✅ 需要回退能力的项目（改坏了能恢复）

不需要 Git 的项目：
  ❌ 一次性实验（跑完就扔）
  ❌ 临时笔记（随手记的）
  ❌ 纯学习练习（网上找的教程跟着做）
  ❌ 太小的代码片段（不到 50 行）
```

## 在 workspace/ 中管理 Git

### 主仓库

整个 AI_Project_Example 用一个 Git 仓库管理：

```bash
# 在 AI_Project_Example/ 根目录初始化
git init
```

### .gitignore 规则

在根目录的 .gitignore 中，控制什么该忽略：

```gitignore
# 始终跟踪
workspace/*/README.md
workspace/*/notes/
lab_book/
tools/
AGENTS.md
CONVENTIONS.md

# 始终忽略
.DS_Store
__pycache__/
*.pyc
.env
.venv/
node_modules/
```

### 每个子项目的 .project-gitconfig

在需要 Git 管理的子项目中创建 `.project-gitconfig`：

```
workspace/my_project/
├── .project-gitconfig    ← 标记"这个项目需要 Git"
├── README.md
├── src/
└── ...
```

`.project-gitconfig` 内容：

```yaml
# 项目 Git 配置
git: true
strategy: commit-per-feature    # commit 粒度策略
protected_files:                # 不允许 AI 修改的文件
  - config/production.yaml
  - .env
```

## 工作流程

### 新建项目时

```
1. 运行 new_project.py 创建骨架（自动带 notes/）
2. 判断是否需要 Git
   - 需要 → 创建 .project-gitconfig，加入 git 管理
   - 不需要 → 不做任何操作，靠主仓库的 .gitignore 控制
```

### 工作过程中

```
如果项目有 .project-gitconfig：
  - 每完成一个功能点，自动 commit
  - commit 消息遵循 CONVENTIONS.md 的规范
  - 不修改 protected_files 中的文件

如果没有 .project-gitconfig：
  - 只在主仓库层面记录
  - 文件变更由主仓库的 git 管理
```

### 回退操作

```
需要回退时：
  - 有 .project-gitconfig → 在子项目目录内 git 操作
  - 没有 .project-gitconfig → 在主仓库操作
  - 都不确定 → 先 git status 看看当前状态
```

## Git Commit 粒度策略

在 `.project-gitconfig` 的 `strategy` 字段定义：

```
commit-per-feature    → 每个功能完成后 commit（推荐大多数项目）
commit-per-session    → 每次对话结束时 commit（适合实验项目）
commit-per-milestone  → 每个里程碑才 commit（适合大型项目）
```

## 命令速查

```bash
# 查看所有项目的 Git 状态
find workspace/ -name ".project-gitconfig" -exec sh -c 'cd "$(dirname "$1")" && echo "--- $(pwd) ---" && git status -s' _ {} \;

# 在某个子项目中 commit
cd workspace/my_project
git add -A && git commit -m "feat: xxx"

# 在主仓库中 commit（非 Git 管理的项目变更）
git add workspace/ lab_book/
git commit -m "chore: 更新项目记录"
```
