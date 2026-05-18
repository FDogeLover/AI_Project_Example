# 通用型 AI 工程的模式

## 文件自描述

AI 理解一个项目最快的方式不是读代码，而是读文件名和目录名。

好的命名：
```
user_authentication.py    ← AI 知道这是用户认证
database_migration.sql    ← AI 知道这是数据库迁移
```

差的命名：
```
helper.py                 ← AI 完全不知道这是干嘛的
utils2.py                 ← 比 utils.py 还模糊
data.csv                  ← 什么数据？给谁用的？
```

**规则：文件名就是它的第一个 docstring。**

## 说明文件紧跟内容

每个目录、每个重要文件旁边放一个说明。AI 扫一遍文件名+说明就知道全貌，不用读任何代码。

```
workspace/
├── README.md         ← "这里是放工作成果的"
├── project_a/
│   ├── README.md     ← "这是一个图像识别项目，用的 PyTorch"
│   └── train.py
└── project_b/
    ├── README.md     ← "这是一个 REST API，用的 FastAPI"
    └── main.py
```

## 分层在任何领域都适用

不分前后端，不分软硬件，"输入→处理→输出"的分层永远成立：

```
Web 后端:     api → services → models
深度学习:     data → model → training → evaluation
单片机:       drivers → logic → communication
文档项目:     research → writing → review → publish
```

**每种工作都可以拆成至少三层。找到你的三层，项目就不会乱。**
