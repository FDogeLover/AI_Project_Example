# 行为准则

## 文件命名

```
entries/    → YYYY-MM-DD-简短标题.md
patterns/   → 编号-模式名称.md（如 001-universal-patterns.md）
mistakes/   → YYYY-MM-DD-简短标题.md
```

## 子项目 README 格式

```markdown
# 项目名

> type: backend | frontend | ml | embedded | script | note | mixed
> status: active | paused | archived
> created: YYYY-MM-DD
> last_active: YYYY-MM-DD
```

## Git 管理

需要 Git 的项目创建 `.project-gitconfig`：

```yaml
git: true
strategy: commit-per-feature    # 或 commit-per-milestone
protected_files: []
```

不需要 Git 的项目不做任何操作。

## 代码约定

- Python 函数/变量: snake_case
- Python 类: PascalCase
- 类型注解必须有
- 解释 why，不解释 what

## 知识类项目结构

```
inbox/        → 一切入口
knowledge/    → 沉淀（patterns/cases/theories）
connections/  → 关系网
```

## 重要原则

- 提问一次一个，不甩串
- 建议要可执行，不空泛
- 新项目必须走完整接入流程
- 先回顾再行动，不要带着记忆空白干活
