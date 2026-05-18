# 实验室守则

## 一键接管

第一次打开这个项目，按这个顺序执行：

```bash
# 1. 运行智能中枢，获取全局状态
python3 tools/scripts/agent_hub.py

# 2. 读取错误教训和经验模式
cat lab_book/mistakes/README.md
cat lab_book/patterns/README.md

# 3. 运行自测确认系统健康
python3 tools/scripts/self_test.py

# 4. 根据 agent_hub 的建议开始工作
```

## 这个工程是什么

一个通用 AI 工程工作台。
后端、前端、深度学习、知识体系、创作工具——都可以在这里做。

## 目录结构

```
workspace/       ← 工作成果（项目）
lab_book/        ← 认知积累（经验、教训、模式）
tools/           ← 工具箱（脚本、模板）
AGENTS.md        ← 你正在读的这个文件
CONVENTIONS.md   ← 行为准则
```

## 核心行为

### 你不是工具，你是协作者
看到新东西就主动理解、主动提问、主动建议。

### 事前自检（每次开始工作前）
```
1. 运行 python3 tools/scripts/agent_hub.py --quick
2. 查 lab_book/mistakes/ → 别犯老错
3. 查 lab_book/patterns/ → 用现成模式
4. 制定执行计划
```

### 项目接入（新项目出现时）
```
1. python3 tools/scripts/project_scanner.py    → 扫描共性
2. 逐个提问了解项目                              → 一次问一个
3. 更新 README、lab_book/entries/               → 记录接入
4. 提出 2-3 个建议                               → 具体可执行
```

### 事后优化（每次完成任务后）
```
- 新错误 → lab_book/mistakes/
- 新模式 → lab_book/patterns/
- 有值得做 skill 的 → 创建
- 有新工具 → tools/scripts/
```

### 系统自省（每 3 次任务后）
```
python3 tools/scripts/agent_hub.py --health
```

## 进化触发机制

```
有新内容 → 触发进化
没新内容 → 不做任何检查
```

## 工具速查

| 工具 | 用途 |
|------|------|
| agent_hub.py | 智能中枢（全局状态 + 建议） |
| auto_evolve.py | 自动进化（检测变更 → 触发进化） |
| new_project.py | 创建新项目（自动接入） |
| project_scanner.py | 扫描项目共性 |
| status_board.py | 状态看板 |
| knowledge_guard.py | 知识保鲜检查 |
| inbox_cleaner.py | inbox 清理 |
| daily_report.py | 生成日报 |
| session_resume.py | 会话恢复 |
| skill_lint.py | skill 质量检查 |
| export_project.py | 导出项目 |
| export_framework.py | 导出框架 |
