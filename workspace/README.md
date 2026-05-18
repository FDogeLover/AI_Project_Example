# 工作空间

这里放你所有的工作成果。

## 目录结构

```
workspace/
├── project_a/        ← 一个具体项目
│   ├── README.md     ← 项目说明
│   ├── notes/        ← 项目特有的记录（决策、进度、想法）
│   └── ...           ← 项目自身的代码和文件
├── project_b/
│   ├── README.md
│   ├── notes/
│   └── ...
├── snippets/         ← 散落的代码片段（还没归入任何项目）
└── notes/            ← 散落的文字笔记（还没归入任何项目）
```

## 知识的两层存放

### 全局知识 → lab_book/
所有项目共享的经验和教训写在这里：
```
lab_book/
├── entries/     ← 通用的思考记录
├── patterns/    ← 跨项目通用的模式
└── mistakes/    ← 所有项目都该避免的错误
```

### 项目知识 → workspace/<项目>/notes/
每个项目特有的记录写在这里：
```
workspace/project_a/notes/
├── 2026-05-15-选型决策.md
├── 2026-05-16-发现的数据问题.md
└── progress.md    ← 项目进度日志
```

### 判断标准

```
这条经验只在这个项目有用？     → 写进 workspace/<项目>/notes/
这条经验所有项目都该知道？     → 写进 lab_book/
不确定？                       → 先写进项目 notes/，以后有重复再提升到 lab_book
```

## 子项目规范

每个子项目 README 必须包含：

```markdown
# 项目名

> type: backend | frontend | ml | embedded | script | note | mixed
> status: active | paused | archived
> created: YYYY-MM-DD
> last_active: YYYY-MM-DD

## 做什么
一句话说明

## 技术栈
列出使用的技术
```

### snippets/ —— 代码片段

放那些"以后可能用到但还没归入项目"的代码：

```
snippets/
├── python/
│   └── async_http_client.py
├── javascript/
│   └── debounce.js
└── c/
    └── uart_read.c
```

按语言分文件夹，每个文件顶部写清楚用途。

## 注意事项

- workspace/ 下不要放工具和脚本，那些去 tools/
- workspace/ 下不要放全局决策记录，那些去 lab_book/
- 每个工作成果旁边放一个说明文件，AI 不用读代码就能知道它是干嘛的
